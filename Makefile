
symbols:
	c4ddev symbols -f file -o lib/c4ddev/res.py

clean:
	rm -v $(shell find lib/ -iname *.pyc)
