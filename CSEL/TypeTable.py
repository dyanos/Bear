from .ASTNativeDef import *

class Type:
	def __init__(self, typename, name):
		self.typename = typename
		self.name = name

	def getTypename(self):
		return self.typename

	def getName(self):
		return self.name


class AliasType(Type):
	def __init__(self, name, oname):
		super(AliasType, self).__init__(typename="alias", name=name)
		self.original = oname

	def getOriginalName(self):
		return self.original


class DefType(Type):
	def __init__(self, name, body):
		super(DefType, self).__init__(typename="DefType", name=name)
		self.body = body

	def getBody(self):
		return self.body


class ClassType(Type):
	def __init__(self, name, typeInfo):
		super(ClassType, self).__init__(typename="class", name=name)
		self.info = typeInfo

	def find(self, name):
		# method또는 attribute에서 해당 name을 검색한다.
		table = self.info["@symbolTable"]
		if name in table:
			return True

		return False


class NamespaceType(Type):
	def __init__(self, name, namespaceInfo):
		super(NamespaceType, self).__init__(typename="namespace", name=name)
		self.info = namespaceInfo

	def find(self, name):
		# method또는 attribute에서 해당 name을 검색한다.
		table = self.info["@symbolTable"]
		if name in table:
			return True

		return False	


class TypeTable:
	def __init__(self):
		# table은 dict
		# key는 type이름, value는 해당 type의 속성정보를 담고 있음(template도)
		self.table = {}
		# backward search를 위해서
		self.backward = {}
		self.dictionary = {}

		# 기본 정보
		self.add(AliasType("char", "System.lang.Char"))
		self.add(AliasType("byte", "System.lang.Byte"))
		self.add(AliasType("int", "System.lang.Integer"))
		self.add(AliasType("long", "System.lang.Long"))
		self.add(AliasType("string", "System.lang.String"))
		self.add(AliasType("float", "System.lang.Float"))
		self.add(AliasType("double", "System.lang.Double"))
		self.add(AliasType("boolean", "System.lang.Boolean"))
		self.add(AliasType("bool", "System.lang.Boolean"))

		self.add(NamespaceType("System", {"@children": ["lang", "out"]}))
		self.add(NamespaceType("System.lang", {"@children": ["Char", "Byte", "Integer", "Long", "String", "Float", "Double", "Boolean"]}))
		self.add(NamespaceType("System.out", {"@children": ["println"]}))

		content = {"@name": "Integer", 
			"@shortname": "int", 
			"@fullname": "System.lang.Integer",
			"@native": True,
		    "@symbolTable": {
				"toString": ASTNativeDef("System.lang.Integer.toString")
			}}
		self.add(ClassType("System.lang.Integer", content))

		content = {"@name": "String", 
			"@shortname": "string", 
			"@fullname": "System.lang.String",
			"@native": True,
		    "@symbolTable": {
				"toString": ASTNativeDef("System.lang.String.toString")
			}}
		self.add(ClassType("System.lang.String", content))

		content = {"@name": "Array", 
			"@fullname": "System.lang.Array",
			"@native": True,
		    "@symbolTable": {
				"toString": ASTNativeDef("System.lang.Array.toString")
			}}
		self.add(ClassType("System.lang.Array", content))

		self.add(DefType("System.out.println", {"@native": True}))
	

	def add(self, element: Type):
		if element.getName() in self.table:
			# 중복?
			print("duplicated symbol! {}".format(element.getName()))
			return

		if element.getTypename() == "alias":
			self.table[element.getName()] = element.getOriginalName()
			self.backward[element.getName()] = element.getName()
		elif element.getTypename() == "class" or \
			element.getTypename() == "namespace":
			self.table[element.getName()] = element
			lastname = element.getName().split(".")[-1]
			self.backward[lastname] = element.getName()
		elif element.getTypename() == "def":
			self.table[element.getName()] = element.getBody()

	def find_backward(self, name):
		if name not in self.backward:
			# 해당 type의 것이 존재하지 않는다.
			return False

		return self.backward[name]
			
	def find(self, name):
		if name not in self.table:
			# 해당 type의 것이 존재하지 않는다.
			return False

		return self.table[name]
	