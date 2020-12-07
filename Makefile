dist:
	( cd docs; make html )
	YES_I_HAVE_THE_RIGHT_TO_USE_THIS_BERKELEY_DB_VERSION=1 ./setup.py sdist

clean:
	rm -rf build dist
	@( cd docs; make clean )
