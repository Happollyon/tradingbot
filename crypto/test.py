import threading
import queue


# function  mimking console
def console(q):
   
    # infinit loop
    while 1:i

        # get input
        cmd = input("> ")
        q.put(cmd)
        
        # leave infinit  loop
        if cmd == 'quit':
            break

#action 
def action_foo():
    print('--> test 1')

#action
def action_bar():
    print('--> test 2')

#action
def invalid_input():
    print('---> unknown command')

#main code
def main():

    #actions conected to function
    cmd_actions = {'foo': action_foo, 'bar': action_bar}
    

    cmd_queue = queue.Queue()

    dj = threading.Thread(target = console, args = (cmd_queue,))
    dj.start()

    while 1:
        cmd = cmd_queue.get()
        if cmd == 'quit':
            break
        action = cmd_actions.get(cmd, invalid_input)
        action()
main()        
