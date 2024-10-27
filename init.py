def save_data(filename):
    with open(filename, 'w') as f:
        f.write(str(33))
    f.close()

def write_history(filename):
    open(filename,'w').close()

save_data('data.txt')
write_history('history.txt')
print("Initializing... Done!")