import wrapt, functools, copy, requests, re, time, json

class Configurator:
	def __init__(self):
		self.vars = {}
		return
	def setvar(self, var, val):
		self.vars[var] = val
	def getvar(self,var):
		return self.vars[var]


def settype(val, types):
	return types(val)

currentConfiguration = Configurator()
currentConfiguration.setvar("manga", "")
currentConfiguration.setvar("chapter", -1)
currentConfiguration.setvar("delay", -1)
currentConfiguration.setvar("sendto", "")
currentConfiguration.setvar("method", "") # get, post, put, discord ... nothing more
defaultConfig = copy.deepcopy(currentConfiguration)

def isConfigured():
	global currentConfiguration, defaultConfig
	for k in currentConfiguration.vars:
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
			return CommandRun( error = True , error_message = "Too many arguments." )
		if(len(args) < arg_min):
			return CommandRun( error = True , error_message = "Too few arguments." )
		return wrapped(*args)
	return wrapper(wrapped)

def Nothing():
	return CommandRun()

def NotifyChapter(chapter, to_read, subtitle, chapter_title):
	global currentConfiguration
	sendmethod = currentConfiguration.getvar("method")
	urlto = currentConfiguration.getvar("sendto")
	manga = currentConfiguration.getvar("manga")
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
	else:
		print("[Error] Your method node is wrong. It must be `get`, `post`, `put` or `discord`.")

@Command
def CheckGithub(*args):
	print("Check GitHub page: https://github.com/lmnyx/mangalib-notifier")
	return CommandRun()

@Command
def NotifierListen(*args):
	global currentConfiguration
	if not isConfigured():
		return CommandRun(error=True, error_message = "Your configuration isn't complete. Check help for help.")
	print("[Listener] Now listening to mangalib.me/"+currentConfiguration.getvar('manga'))
	while(True):
		res = requests.get("https://mangalib.me/"+currentConfiguration.getvar('manga'))
		if(res.status_code != 200):
			return CommandRun( error = True, error_message = "Listener hit {0} error while requesting the manga.".format(str(res.status_code)) )
		p = re.compile('data-number="(\d+)"')
		p2 = re.compile('data-manga-name="(\w+)"')
		p3 = re.compile('data-volume="(\d+)"')
		nvm = p2.search(res.text).group(1)
		rtx = p.search(res.text)
		idm = p3.search(res.text).group(1)
		chap = int(rtx.group(1))
		pog = re.compile('<a class="link-default" title="(\w+)"').search(res.text).group(1)
		if(chap > currentConfiguration.getvar('chapter')):
			currentConfiguration.setvar('chapter', currentConfiguration.getvar('chapter')+1)
			print("["+currentConfiguration.getvar('manga').title()+"] Chapter #"+str(currentConfiguration.getvar('chapter'))+" came out!")
			NotifyChapter(currentConfiguration.getvar('chapter'), idm, nvm,pog)
		time.sleep(currentConfiguration.getvar('delay'))
	return CommandRun()

@Command(arg_min=2, arg_max=2)
def SetConfig(*args):
	global currentConfiguration, defaultConfig
	if not (args[0] in defaultConfig.vars): return CommandRun( error = True , error_message = "There is no such configuration node. ({0})".format(args[0]) )
	currentConfiguration.setvar(args[0], settype(args[1], type(defaultConfig.vars[args[0]])))
	print("[Configurator] Node {0} is now set to `{1}`.".format(args[0], currentConfiguration.getvar(args[0])))
	return CommandRun()


@Command
def AutoConfigurator(*args):
	global currentConfiguration, defaultConfig
	for k in defaultConfig.vars:
		print(k.title()+": ", end="")
		i = input()
		currentConfiguration.setvar(k, settype(i, type(defaultConfig.vars[k])))
	print("[AutoNode] Configuration finished.")
	return CommandRun()

@Command
def SetNaruto(*args):
	currentConfiguration.setvar("manga", "naruto")
	currentConfiguration.setvar("chapter", "700")
	currentConfiguration.setvar("delay", "300")
	print("[] Naruto setup loaded.")
	return CommandRun()

@Command(arg_min=1, arg_max=1)
def SaveCfg(*args):
	global currentConfiguration
	cfg = WriteCfg(currentConfiguration.vars)
	with open(args[0]+".ml-cfg", "w") as f:
		f.write(cfg)
	print("["+args[0].title()+"] Saved.")
	return CommandRun()

@Command(arg_min=1, arg_max=1)
def LoadCfg(*args):
	cfg = {}
	cfg_r = ""
	with open(args[0]+".ml-cfg", "r") as f:
		cfg_r = f.read()
	cfg = ReadCfg(cfg_r)
	for k in cfg:
		currentConfiguration.setvar(k, settype(cfg[k], type(currentConfiguration.vars[k])))
	print("["+args[0].title()+"] Loaded.")
	return CommandRun()

RegisteredCommands = {
	"help": {"break": False, "run": CheckGithub},
	"listen": {"break": False, "run": NotifierListen},
	"setnode": {"break": False, "run": SetConfig},
	"autonode": {"break": False, "run": AutoConfigurator},
	"naruto": {"break": False, "run": SetNaruto},
	"save": {"break": False, "run": SaveCfg},
	"load": {"break": False, "run": LoadCfg},
	"exit": {"break": True, "run": Nothing},
}

def run(cmd):
	args = cmd = cmd.split(' ')
	if(cmd[0] in RegisteredCommands): return RunResponse(RegisteredCommands[args[0]]['break'], ToRun=RegisteredCommands[args[0]]['run'])
	return RunResponse(False)