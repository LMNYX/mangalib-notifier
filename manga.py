import time, _mnserve, os

listening_input = True
while(listening_input):
	print("> ", end="")
	try:
		cmd = input()
	except KeyboardInterrupt:
		print("\nBye!")
		os._exit(0)
	cmdrun = _mnserve.run(cmd)
	args = cmd.split(' ')
	del args[0]
	if(cmdrun.ToRun != None):
		try:
			funcrun = cmdrun.ToRun(*args)
		except KeyboardInterrupt:
			print("[KeyboardInterrupt] Exited the function.")
		if(funcrun.error):
			print('[Error] '+funcrun.error_message)
	else:
		continue
	if(cmdrun.escapeLoop): listening_input = False

print("[Core] Listening Loop ended.")