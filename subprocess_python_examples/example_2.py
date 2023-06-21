import subprocess

# if you want whole command in one line you can put shell=True

# result = subprocess.run(["ls", "-la"], capture_output=True, text=True)
# capture_output will capture the result in result variable and then we can print the result.
# print(result.stdout.decode())  # if text=True is set then no need to decode the result
# print(result.stdout)

#  if you want python to through an exception if external command fails.Because python wont throw an exception if command fails(return non zero code)
# result = subprocess.run(["ls", "-la"], capture_output=True, text=True, check=True)
# print(result.stderr)



#  if want to write in a file
# with open("log.txt", "w") as file:
#     result = subprocess.run(["ls", "-la"], stdout=file, text=True)


# we can give the output of one command to input to other command.

p1 = subprocess.run(["cat", "test.txt"], capture_output=True, text=True)
print(p1.stdout)
p2 = subprocess.run(["grep", "-n", "test"], capture_output=True, text=True, check=True, input=p1.stdout)

print(p2.stdout)
