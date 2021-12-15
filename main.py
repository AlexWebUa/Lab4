from bs4 import BeautifulSoup
import requests
from tkinter import *

soup = BeautifulSoup()

master = Tk()
master.geometry('390x50')
master.resizable(height=False, width=False)
entry = Entry(master)
entry.place(x=10, y=10, width=280, height=25)
entry.focus()
soup.prettify()


# считывание всех ссылок и колличества ссылок на страницы
def read_all_pages(all_links, links_count, visited_links, site):
    flag = True
    for key in visited_links.keys():
        if visited_links.get(key) is False:
            flag = False
            break
    if flag:
        return
    links_been_temp = {}
    for key in visited_links.keys():
        # print(key)
        if visited_links.get(key) is False:
            visited_links.update({key: True})
            try:
                soup = BeautifulSoup(requests.get(key).text, 'html.parser')
            except requests.exceptions.ChunkedEncodingError:
                # print(key)
                continue
            except KeyboardInterrupt:
                # print(key)
                continue
            except requests.exceptions.MissingSchema:
                continue
            except requests.exceptions.InvalidSchema:
                continue
            links = soup.find_all('a')
            temp = []
            for link in links:
                try:
                    link_str = str(link['href'])
                except KeyError:
                    # print(link)
                    continue
                if (((link_str[0] == "/" and link_str[0:2] != "//") or link_str[0] == "#") and len(link_str) != 1) \
                        or link_str[0:len(site)] == site or link_str[0:3] == "../":
                    if link_str not in temp:
                        temp.append(link_str)
                        if link_str[0] == "/":
                            link_str = site + link_str
                        if link_str[0] == "#":
                            link_str = site + "/" + link_str
                        if link_str[0:3] == "../":
                            link_str = site + "/" + link_str[3:len(link_str)]
                        if link_str[len(link_str) - 1:len(link_str)] == "/":
                            link_str = link_str[0:len(link_str) - 1]
                        links_count.update({key: (links_count.get(key) + 1)})
                        tmp = []
                        if link_str not in visited_links.keys():
                            links_been_temp.setdefault(link_str, False)
                        if all_links.get(link_str) is not None:
                            tmp = all_links.get(link_str)
                        if link_str != key:
                            tmp.append(key)
                            all_links.update({link_str: tmp})
                        if link_str not in links_count.keys():
                            links_count.setdefault(link_str, 0)

    for link in links_been_temp.keys():
        visited_links.update({link: False})
    read_all_pages(all_links, links_count, visited_links, site)
    return

# определитель матрицы
def determinant(xn, xnd, page_ranks):
    i = 0
    matrix = [[0] * len(xn.keys())] * len(xn.keys())
    columns = []
    for x in xn.keys():
        for xx in xn.get(x).keys():
            matrix[i].append(xn.get(x).get(xx) * page_ranks.get(xx))
        matrix[i].append(xnd.get(x))
        i += 1
    for j in range(len(matrix[0])):
        sum = 0
        for q in range(len(matrix)):
            sum += matrix[q][j]
        columns.append(sum)
    return columns

# решаем систему линейных уравнений методом Якоби
def SLAR(links, links_count):
    xn = {}
    xnd = {}
    page_ranks = {}
    for link in links.keys():
        tmp = {}
        for sub_link in links_count.keys():
            if sub_link in links.get(link):
                tmp.update({sub_link: (0.5 / links_count.get(sub_link))})
            else:
                tmp.update({sub_link: 0})
        xnd.update({link: (1 - 0.5)})
        xn.update({link: tmp})

    for x in xn.keys():
        sum = xnd.get(x)
        for xx in xn.get(x).keys():
            sum += (xn.get(x).get(xx) * xnd.get(x))
        page_ranks.update({x: sum})
    flag = True
    while flag:
        page_ranks_n = {}
        for x in xn.keys():
            sum = xnd.get(x)
            for xx in xn.get(x).keys():
                sum += (xn.get(x).get(xx) * page_ranks.get(xx))
            page_ranks_n.update({x: sum})

        flag = False
        B1 = determinant(xn, xnd, page_ranks)
        B2 = determinant(xn, xnd, page_ranks_n)
        for i in range(len(B1)):
            if abs(B1[i] - B2[i]) > 0.001:
                flag = True
        page_ranks = page_ranks_n
    return page_ranks


def read_site():
    site = entry.get()
    links = {site: []}
    links_count = {site: 0}
    visited_links = {site: False}
    read_all_pages(links, links_count, visited_links, site)

    page_ranks = SLAR(links, links_count)
    print(page_ranks)


buttonOpen = Button(master, text="Start", width=10, command=read_site)
buttonOpen.place(x=300, y=10)

mainloop()

