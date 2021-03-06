#!/usr/bin/env python3

from configdb import *
import unittest

#  Kludge in order to use FileNotFoundError in Python2
try: FileNotFoundError
except NameError:
	FileNotFoundError=IOError

class test_configdb(unittest.TestCase):

	mandatoryKeys = [
		'username',
		'database',
		'password',
		]

	def addFile(self, file) :
		self.toRemove.append(file)

	def setUp(self) :
		self.toRemove=[]
		self.data = namespace(
			default = namespace(
				(key, 'my'+key) for key in self.mandatoryKeys),
			alternative=namespace(
				(key, 'other'+key) for key in self.mandatoryKeys),
			)
		self.data.dump('config.yaml')
		self.addFile('config.yaml')
		self.oldEnviron = os.environ.copy()

	def tearDown(self):
		for f in self.toRemove:
			try: os.unlink(f)
			except FileNotFoundError: pass
			except OSError: pass
		os.environ.clear()
		os.environ.update(self.oldEnviron)

	def test_configdb_notExistingConfigFile_generatesAnUnsetOne_withDefaultParams(self) :
		self.addFile('nonexistingconfig')
		with self.assertRaises(MissingValue) :
			configdb(configfile='nonexistingconfig')
		autogenerated = namespace.load('nonexistingconfig')
		self.assertDictEqual(
			dict(
				default=dict(
					dbname=None,
					user=None,
					pwd=None,
				)),
			autogenerated)

	def test_configdb_notExistingConfigFile_generatesAnUnsetOne(self) :
		self.addFile('nonexistingconfig')
		required='param1 param2 param3'.split()
		with self.assertRaises(MissingValue) :
			configdb(required=required, configfile='nonexistingconfig')
		autogenerated = namespace.load('nonexistingconfig')
		self.assertDictEqual(
			dict(
				default=dict(
					param1=None,
					param2=None,
					param3=None,
				)),
			autogenerated)

	def test_configdb_takesDefaultProfile(self) :
		config=configdb(configfile='config.yaml', required=self.mandatoryKeys)
		self.assertDictEqual(config, self.data.default)

	def test_configdb_explicitProfile_takesAlternativeData(self) :
		config=configdb(profile='alternative',configfile='config.yaml', required=self.mandatoryKeys)
		self.assertDictEqual(config, self.data.alternative)

	def test_configdb_createsSubdirs(self) :
		self.addFile("asubdir/anothersubdir/config.yaml")
		self.addFile("asubdir/anothersubdir")
		self.addFile("asubdir")
		with self.assertRaises(MissingValue) :
			configdb(configfile='asubdir/anothersubdir/config.yaml',
				required=self.mandatoryKeys)
		self.assertTrue(os.access('asubdir/anothersubdir/config.yaml',os.F_OK))
		autogenerated = namespace.load('asubdir/anothersubdir/config.yaml')
		self.assertDictEqual(autogenerated,
			dict( default=dict((key, None) for key in self.mandatoryKeys)))

	def test_configdb_badProfile(self) :
		with self.assertRaises(BadProfile) as e:
			configdb(profile='badprofile',configfile='config.yaml')
		self.assertEqual(str(e.exception.args[0]),
			"Database profile 'badprofile' not availabe in 'config.yaml', "
			"try with: alternative, default"
			)

	def test_configdb_environment_takesAlternativeData(self) :
		os.environ['CONFIGDB_PROFILE']='alternative'
		config=configdb(configfile='config.yaml', required=self.mandatoryKeys)
		self.assertDictEqual(config, self.data.alternative)

	def test_defaultConfigDbFile_linux(self) :
		self.assertEqual(
			os.path.join(
				os.environ['HOME'],
				'.config',
#				'somenergia',
				'configdb',
				'1.0',
				'configdb.yaml',
			),
			defaultConfigDbFile())


if __name__ == '__main__':
	import sys
	sys.exit(unittest.main())


