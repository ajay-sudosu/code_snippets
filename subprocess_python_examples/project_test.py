from subprocess import Popen, PIPE

sudo_password = 'ajaysingh03'
command = 'docker ps'.split()
p = Popen(['sudo', '-Ssd'] + command, stdin=PIPE, stderr=PIPE,
          universal_newlines=True)
result = p.communicate(sudo_password + '\n')
# print(out)
# print(err)
a = 10