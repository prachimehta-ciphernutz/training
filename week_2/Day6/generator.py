def read_file(file_path):
    with open(file_path, "r") as file:
        for line in file:
            yield line.strip()

def process_file(file_path):
    line_count = 0
    for line in read_file(file_path):
        if line:
            line_count += 1
    return line_count

count = process_file("/home/cn/Documents/task/week_1/Day5/people-100.csv")
print("Total valid count:", count)