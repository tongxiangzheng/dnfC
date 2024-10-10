import autotest_src
info="acpid acpid 2.0.34 3.oe2403"
info=info.split(" ")
autotest_src.autotest_src(info[0],info[1],info[2],info[3],checkExist=False)
