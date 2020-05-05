import wrapt, functools, copy, requests, re, time, json, os
from collections import namedtuple
class Configurator:
	def __init__(self):
		self.vars = {}
		return
	def setvar(self, var, val):
		self.vars[var] = val
	def getvar(self,var):
		return self.vars[var]

class Empty:
	def __init__(self):
		return

def settype(val, types):
	return types(val)

currentConfiguration = Configurator()
currentConfiguration.setvar("manga", "")
currentConfiguration.setvar("chapter", -1)
currentConfiguration.setvar("delay", -1)
currentConfiguration.setvar("url", "")
currentConfiguration.setvar("method", "") # get, post, put, discord ... nothing more
defaultConfig = copy.deepcopy(currentConfiguration)

localization = {
	"save_autosave": "Autosaved.",
	"save_save": "Saved.",
	"save_load": "Loaded.",
	"save_autos": "You cannot save autos",
	"save_autoload": "Autoloaded.",
	"deprecated_method": "{0} is deprecated, use {1} instead.",
	"notify_method_wrong": "Your method is wrong, it must be `get, `post`, `put` or `discord`.",
	"listener_start": "Now listening to {0}",
	"listener_new": "New chapter #{0} came out!",
	"listener_autoset": "OK. Now waiting chapter to be greater than {0}.",
	"listener_configure": "Your configuration isn't complete.",
	"listener_error": "Listener hit {0} error.",
	"node_existance": "There is no such node named `{0}`.",
	"node_set": "Node {0} is now equals {1}.",
	"node_auto_complete": "Autonode setup complete.",
	"cmd_many": "Too many arguments",
	"cmd_few": "Too few arguments",
	"cmd_empty": "You cannot leave argument(s) empty.",
	"no_chapters": "Manga you provided {0} do not have any chapter yet."
}

lclz = namedtuple("Localization", localization.keys())(*localization.values())

def LocModify(stra, val):
	global localization, lclz
	localization[stra] = val
	lclz = namedtuple("Localization", localization.keys())(*localization.values())

LoadedSaveFile = ""

def isConfigured():
	global currentConfiguration, defaultConfig
	skippable = ["chapter"]
	for k in currentConfiguration.vars:
		if k in skippable: continue
		if(currentConfiguration.getvar(k) == defaultConfig.getvar(k)):
			print(k+" = "+str(defaultConfig.getvar(k))+" / "+str(currentConfiguration.getvar(k)))
			return False
	return True

def ReadCfg(cfg_string):
	cfg_lines = cfg_string.split('\n')
	cfg = {}
	for line in cfg_lines:
		line = line.split(':',1)
		if(len(line) > 1):
			cfg[line[0]] = line[1]
	return cfg

def WriteCfg(cfg_dict):
	cfg_string = ""
	ld = len(cfg_dict)
	cr = 1
	for k in cfg_dict:
		if(cr < ld):
			cfg_string = cfg_string + k +":"+str(cfg_dict[k])+"\n"
		else:
			cfg_string = cfg_string + k +":"+str(cfg_dict[k])
		cr += 1
	return cfg_string
class RunResponse(object):
	def __init__(self, isEscapingLoop, ToRun = None):
		self.escapeLoop = isEscapingLoop
		self.ToRun = ToRun

class CommandRun(object):
	def __init__(self, error = False, error_message = "No error."):
		self.error = error
		self.error_message = error_message

def Command(wrapped = None, arg_max = 0, arg_min = 0):
	if wrapped is None:
		return functools.partial(Command,arg_max=arg_max, arg_min=arg_min)

	@wrapt.decorator
	def wrapper(wrapped, instance, args, kwargs):
		if(len(args) > arg_max):
			return CommandRun( error = True , error_message = lclz.cmd_many )
		if(len(args) < arg_min):
			return CommandRun( error = True , error_message = lclz.cmd_few )
		for a in args:
			if not a:
				return CommandRun( error = True , error_message = lclz.cmd_empty )
		return wrapped(*args)
	return wrapper(wrapped)

def _cfgsave(fname):
	global currentConfiguration, LoadedSaveFile
	cfg = WriteCfg(currentConfiguration.vars)
	try:
		with open(fname+".ml-cfg", "w") as f:
			f.write(cfg)
	except Exception as e:
		return CommandRun( error = True, error_message = str(e) )
	LoadedSaveFile = fname
	print("["+fname.title()+"] {0}".format(lclz.save_autosave))
	return CommandRun()

def _cfgload(fname):
	global LoadedSaveFile
	cfg = {}
	cfg_r = ""
	try:
		with open(fname+".ml-cfg", "r") as f:
			cfg_r = f.read()
	except Exception as e:
		return CommandRun( error = True, error_message = str(e) )
	cfg = ReadCfg(cfg_r)
	deprecated = {"sendto": "url"}
	for k in cfg:
		deprecated_one = False
		if(k in deprecated):
			print('[LoadCFG] '+ lclz.deprecated_method.format(k, deprecated[k]))
			deprecated_one = True
		if deprecated_one:
			currentConfiguration.setvar(deprecated[k], settype(cfg[k], type(currentConfiguration.vars[deprecated[k]])))
		else:
			currentConfiguration.setvar(k, settype(cfg[k], type(currentConfiguration.vars[k])))
	LoadedSaveFile = fname
	print("["+fname.title()+"] {0}".format(lclz.save_autoload))
	return CommandRun()

def Nothing():
	return CommandRun()

def NotifyChapter(chapter, to_read, subtitle, chapter_title):
	global currentConfiguration, LoadedSaveFile
	sendmethod = currentConfiguration.getvar("method")
	urlto = currentConfiguration.getvar("url")
	manga = currentConfiguration.getvar("manga")
	print("https://mangalib.me/uploads/cover/"+manga+"/cover/cover_250x350.jpg")
	readUrl = "https://mangalib.me/{0}/v{1}/c{2}".format(manga,to_read,chapter)
	if(sendmethod == "get"):
		requests.get(urlto, params={'manga': manga, 'chapter': chapter, "to_read": readUrl})
	elif(sendmethod == "post"):
		requests.post(urlto, data={'manga': manga, 'chapter': chapter, "to_read": readUrl})
	elif(sendmethod == "put"):
		requests.put(urlto, data={'manga': manga, 'chapter': chapter, "to_read": readUrl})
	elif(sendmethod == "discord"):
		req = {
			"username": "MangaLib",
			"avatar_url": "https://mangalib.me/icons/android-icon-192x192.png",
			"embeds": [
			{
			"title": subtitle,
			"url": "https://mangalib.me/"+currentConfiguration.getvar("manga"),
			"description": "Вышла новая глава!",
			"thumbnail": {"url": "https://mangalib.me/uploads/cover/"+manga+"/cover/cover_250x350.jpg"},
			"fields": [{
				"name": "Начинай читать главу №"+str(chapter)+" - "+chapter_title,
				"value": "[Нажмите что бы читать сейчас]({0})".format(readUrl)
			}]
			}
			]
		}
		requests.post(urlto,data=json.dumps(req), headers={"Content-Type": "application/json"})
	elif(sendmethod == "log"):
		print(f'[NEW] {subtitle}: Chapter {chapter} ({chapter_title}) came out! Read here {readUrl}')
	else:
		print("[Error] {0}".format(lclz.notify_method_wrong))

@Command
def CheckGithub(*args):
	print("Check GitHub page: https://github.com/lmnyx/mangalib-notifier")
	return CommandRun()

@Command
def NotifierListen(*args):
	global currentConfiguration
	if not isConfigured():
		return CommandRun(error=True, error_message = lclz.listener_configure)
	print("[Listener] {0}".format(" mangalib.me/"+currentConfiguration.getvar('manga')))
	while(True):
		is_first = currentConfiguration.getvar('chapter') == -1
		res = requests.get("https://mangalib.me/"+currentConfiguration.getvar('manga'))
		if(res.status_code != 200):
			return CommandRun( error = True, error_message = lclz.listener_error.format(str(res.status_code)) )
		p = re.compile('data-number="(\d+)"')
		p2 = re.compile('window.__MANGA__ = {"id":(\d+),"name":"(.*)",')
		p3 = re.compile('data-volume="(\d+)"')
		nvm = list(p2.findall(res.text)[0])
		if(len(nvm) > 1):
			nvm = nvm[1]
		rtx = p.search(res.text)
		print(str(rtx) + " \\\\ "+ str(type(rtx)))
		if(type(rtx) == re.Match):
			rtx = rtx.group(1)
		idm = p3.search(res.text)
		if(type(idm) == re.Match):
			idm = idm.group(1)
		if(rtx != None):
			chap = int(rtx)
		else:
			return CommandRun( error = True , error_message = lclz.no_chapters.format(currentConfiguration.manga))
		pog = re.compile('<a class="link-default" title="(.*)"').search(res.text).group(1)
		print(str(pog))
		if(chap > currentConfiguration.getvar('chapter')):
			currentConfiguration.setvar('chapter', chap)
			if not (is_first):
				print("["+currentConfiguration.getvar('manga').title()+"] "+lclz.listener_new.format(str(chap)))
				_cfgsave(LoadedSaveFile)
				NotifyChapter(chap, idm, nvm,pog)
			else:
				print("[Listener] "+lclz.listener_autoset.format(str(chap)))
				_cfgsave(LoadedSaveFile)
		time.sleep(currentConfiguration.getvar('delay'))
	return CommandRun()

@Command(arg_min=2, arg_max=2)
def SetConfig(*args):
	global currentConfiguration, defaultConfig
	if not (args[0] in defaultConfig.vars): return CommandRun( error = True , error_message = lclz.node_existance.format(args[0]) )
	currentConfiguration.setvar(args[0], settype(args[1], type(defaultConfig.vars[args[0]])))
	print("[Configurator] "+lclz.node_set.format(args[0], currentConfiguration.getvar(args[0])))
	return CommandRun()


@Command
def AutoConfigurator(*args):
	global currentConfiguration, defaultConfig
	for k in defaultConfig.vars:
		print(k.title()+": ", end="")
		i = input()
		currentConfiguration.setvar(k, settype(i, type(defaultConfig.vars[k])))
	print("[AutoNode] "+lclz.node_auto_complete)
	return CommandRun()

@Command(arg_min=0, arg_max=1)
def SaveCfg(*args):
	global currentConfiguration, LoadedSaveFile
	args = list(args)
	if(LoadedSaveFile != "" and len(args) == 0): args.append(LoadedSaveFile)
	if(args[0] == "autoload" or args[0] == "autolisten"): return CommandRun( error = True , error_message = "You cannot save autos." )
	cfg = WriteCfg(currentConfiguration.vars)
	try:
		with open(args[0]+".ml-cfg", "w") as f:
			f.write(cfg)
	except Exception as e:
		return CommandRun( error = True, error_message = str(e) )
	LoadedSaveFile = args[0]
	print("["+args[0].title()+"] "+lclz.save_save)
	return CommandRun()

@Command(arg_min=1, arg_max=1)
def LoadCfg(*args):
	global LoadedSaveFile
	if(args[0] == "autoload" or args[0] == "autolisten"): return CommandRun( error = True , error_message = "You cannot load autos." )
	cfg = {}
	cfg_r = ""
	try:
		with open(args[0]+".ml-cfg", "r") as f:
			cfg_r = f.read()
	except Exception as e:
		return CommandRun( error = True, error_message = str(e) )
	cfg = ReadCfg(cfg_r)
	deprecated = {"sendto": "url"}
	for k in cfg:
		deprecated_one = False
		if(k in deprecated):
			print('[LoadCFG] '+lclz.deprecated_method.format(k,deprecated[k]))
			deprecated_one = True
		if deprecated_one:
			currentConfiguration.setvar(deprecated[k], settype(cfg[k], type(currentConfiguration.vars[deprecated[k]])))
		else:
			currentConfiguration.setvar(k, settype(cfg[k], type(currentConfiguration.vars[k])))
	LoadedSaveFile = args[0]
	print("["+args[0].title()+"] "+lclz.save_load)
	return CommandRun()

RegisteredCommands = {
	"help": {"break": False, "run": CheckGithub},
	"listen": {"break": False, "run": NotifierListen},
	"setnode": {"break": False, "run": SetConfig},
	"autonode": {"break": False, "run": AutoConfigurator},
	"save": {"break": False, "run": SaveCfg},
	"load": {"break": False, "run": LoadCfg},
	"exit": {"break": True, "run": Nothing},
}

def run(cmd):
	args = cmd = cmd.split(' ')
	if(cmd[0] in RegisteredCommands): return RunResponse(RegisteredCommands[args[0]]['break'], ToRun=RegisteredCommands[args[0]]['run'])
	return RunResponse(False)


# AFTER LOADING
###
if(os.path.isfile("locmod.json")):
	print("[Loc] Localization modifier found. Loading..")
	lm = open('locmod.json')
	try:
		_temploc = json.loads(lm.read())
		lm.close()
		for i in _temploc:
			LocModify(i, _temploc[i])
	except json.decoder.JSONDecodeError:
		print('[Loc] locmod file is corrupted.')
if(os.path.isfile("autoload.ml-cfg")): _cfgload("autoload")
if(os.path.isfile("autolisten.ml-cfg")):
	_cfgload("autolisten")
	NotifierListen()
	os._exit(0)