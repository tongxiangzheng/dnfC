import autotest_src
info="evolution-data-server evolution-data-server 3.44.4 0ubuntu1.1"
info=info.split(" ")
autotest_src.autotest_src(info[0],info[1],info[2],info[3],checkExist=False)
