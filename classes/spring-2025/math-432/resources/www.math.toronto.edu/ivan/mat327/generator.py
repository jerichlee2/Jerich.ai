import markdown2
import os

pages = {}
order = {}
for root, dirs, files in os.walk("./pages"):
    for file in files:
        if os.path.splitext(file)[1] == '.md':
            order[int(os.path.splitext(file)[0][:1])] = os.path.splitext(file)[0][2:]
            pages[os.path.splitext(file)[0][2:]] = os.path.join(root, file)

navbar = ''
content = ''

for i in range(len(order)):
    with open(pages[order[i]], 'r') as data:
        title_line = data.readline()
        page_title = title_line[2:-1]
        page_content = markdown2.markdown(title_line + data.read(), extras=["fenced-code-blocks", "tables"])
        navbar += "<button id='nav_{0}' class='navbar_button tablink' onclick=\"navbar(event,'{0}')\">{1}</button>\n".format(order[i],page_title)
        content += "<div id='{0}' class='container border_box content'>\n".format(order[i]) + page_content + "\n</div>\n"
    data.close()

navbar += "<button class='navbar_button icon' onclick=\"toggleNavMenu()\">&#9776;</button>"

output_file = open('index.html', 'w')
template = open('./templates/template.html', 'r')

output = template.read().replace('<!--CONTENT-->', content).replace('<!--NAVBAR-->', navbar)

output_file.write(output)
