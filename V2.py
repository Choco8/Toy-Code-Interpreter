import sys
import re
class program:
	def __init__(self,phrase):
		self.comp_stmt=CompoundStmt(phrase)

	def eval(self,state):
		self.comp_stmt.eval(state)


class CompoundStmt:
	def __init__(self,phrase):
		self.stmts=[]
		counter=0
		j=0
		#print(phrase)
		str2=[]
		for x in phrase:
			if x.find(";")<0:
				x=x+';'
			str2.append(x)			
		phrase=str2
		#print(phrase)
		while(j<len(phrase)):
			#print(phrase[j])
			if (phrase[j][0:3]=='if '):
				self.if_block=[]
				for i in range(j,len(phrase)):
					self.if_block.append(phrase[i].strip())
					if (phrase[i][0:3]=='fi;'):
						counter-=1
					if (phrase[i][0:3]=='if '):
						counter+=1
					#print(counter)
					if (counter==0): 
						break
				j=i+1
				#print(self.if_block)
				self.stmts.append(Stmt.build(self.if_block))

			if (phrase[j][0:6]=='while '):
				self.while_block=[]
				for i in range(j,len(phrase)):
					self.while_block.append(phrase[i].strip())
					if (phrase[i][0:6]=='while '):
						counter+=1
					if (phrase[i][0:5]=='done;'):
						counter-=1
					#print(counter)
					if (counter==0): 
						break
				j=i+1
				self.stmts.append(Stmt.build(self.while_block))

			if (phrase[j][0:9]=='function '):
				self.func_block=[]
				for i in range(j,len(phrase)):
					self.func_block.append(phrase[i].strip())
					if (phrase[i][0:9]=='function '):
						counter+=1
					if (phrase[i][0:4]=='end;'):
						counter-=1
					print(counter)
					if (counter==0): 
						break
				j=i+1
				#print(self.func_block)
				self.stmts.append(Stmt.build(self.func_block))

			print(phrase[j])
			if(j<len(phrase)):
				self.stmts.append(Stmt.build(phrase[j].strip(";")))
			j+=1	
	
	def eval(self,state):
		for s in self.stmts:
			s.eval(state)


class Stmt:

	def build(s):
		if (s[0][0:3]=='if '):
			return IfelseStmt(s)
		elif (s[0][0:6]=='while '):
			return WhileStmt(s)
		elif (s[0][0:9]=='function '):
			return funcStmt(s)
		elif (s[0:6]=='print '):
			return printStmt(s)
		elif (s[0:8]=='println '):
			return printlnStmt(s)
		else:
			return AsgnStmt(s)

	
class funcStmt(Stmt):
	def __init__(self,s):
		str1 = ' '.join(s)
		self.arguments=parameter(s[0])
		for i in s:
			if i.find("return ") >=0:
				self.k=i.split()
		f=re.findall(r"(?<=begin;) (.*?) (?=return)", str1)
		print(f)
		self.func_part=CompoundStmt(list(filter(None,f[0].split(";"))))
		
	def eval(self,newstate):
		if self.k[1].isalpha():
			return newstate(k[1])
		else:
			return 0

class IfelseStmt(Stmt):
	def __init__(self,s):
		str1 = ' '.join(s)
		self.flag=Cond(s[0])
		
		If_part=re.findall(r"(?<=then;) (.*?) (?=else;)", str1)
		self.left=CompoundStmt(list(filter(None,If_part[0].split(";"))))
		else_part=re.findall(r"(?<=else;) (.*?) (?=fi;)", str1)
		self.right=CompoundStmt(list(filter(None,else_part[0].split(";"))))
	
	def eval(self,state):
		#print(self.flag.eval(state))
		if self.flag.eval(state):
			self.left.eval(state)
		else:
			self.right.eval(state)


class WhileStmt(Stmt):
	def __init__(self,s):
		
		str1 = ' '.join(s)
		#print(str1)
		self.flag=Cond(s[0])
		While_part=re.findall(r"(?<=do;) (.*?) (?=done;)", str1)
		self.content=CompoundStmt(list(filter(None, While_part[0].split(";"))))
	
	def eval(self,state):
		#print(self.flag.eval(state))
		while self.flag.eval(state):
			self.content.eval(state)
		
class parameter(funcStmt):
	def __init__(self,s):
		self.exps=[]
		cond=s.split()
		p1=cond[1].split("(")
		p2=p1[1].split(")")
		parameters=p2[0].split(",")
		for i in parameters:
			self.exps+=[Expression.build(i)]
	def eval(self,state):
		a=[]
		for i in self.exps:
			a+=[state[i]]
		return a
	


class Cond(IfelseStmt):
	def __init__(self,s):
		self.cond=s.split()

		if self.cond[1].find(">") >=0:
			exp1,exp2=self.cond[1].split(">")
			self.exp1=Expression.build(exp1)
			self.exp2=Expression.build(exp2)
		
		if self.cond[1].find("<") >=0:
			exp1,exp2=self.cond[1].split("<")
			self.exp1=Expression.build(exp1)
			self.exp2=Expression.build(exp2)
		
		if self.cond[1].find("==") >=0:
			exp1,exp2=self.cond[1].split(":=")
			self.exp1=Expression.build(exp1)
			self.exp2=Expression.build(exp2)
		
		if self.cond[1].find("!=") >=0:
			exp1,exp2=self.cond[1].split("!=")
			self.exp1=Expression.build(exp1)
			self.exp2=Expression.build(exp2)
	
	def eval(self,state):
		if self.cond[1].find(">") >=0:
			return self.exp1.eval(state)>self.exp2.eval(state)
		if self.cond[1].find("<") >=0:
			return self.exp1.eval(state)<self.exp2.eval(state) 
		if self.cond[1].find("==") >=0:
			return self.exp1.eval(state)==self.exp2.eval(state) 
		if self.cond[1].find("!=") >=0:
			return self.exp1.eval(state)!=self.exp2.eval(state)  



class AsgnStmt(Stmt):
	def __init__(self,s):
		#print(s)
		var,exp=s.split("=")
		self.var=var.strip()
		self.exp=Expression.build(exp)

	def eval(self,state):
		state[self.var]=self.exp.eval(state)

class printStmt(Stmt):
	def __init__(self,s):
		k=s.split()
		self.exp=Expression.build(k[1].strip(";"))

	def eval(self,state):
		print(self.exp.eval(state),end=' ')

class printlnStmt(Stmt):
	def __init__(self,s):
		k=s.split()
		self.exp=Expression.build(k[1].strip(";"))

	def eval(self,state):
		print(self.exp.eval(state))

class Expression:
	def build(s):
		s=s.strip()
		#print(s)
		if s.find("+") >=0:
			return PlusExp(s)
		elif s.find("-") >=0:
			return SubExp(s)
		elif s.find("*") >=0:
			return MulExp(s)
		elif s.find("/") >=0:
			return DivExp(s)
		elif s.find("(")<0 & s[0].isalpha():
			return VarExp(s)
		elif s.find("\"")>=0:
			return StringExp(s)
		elif s.find("(") >=0:
			return funcExp(s)
		else:
			return ConstExp(s)

class funcExp(Expression):
	def __init__(self, s):
		self.var= s.strip()

	def eval(self,newstate):
		#print(state[self.var])
		return self.var.eval(newstate)

class ConstExp(Expression):
	def __init__(self,s):
		self.value=int(s)

	def eval(self,s):
		return self.value

class VarExp(Expression):
	def __init__(self, s):
		self.var= s.strip()

	def eval(self,state):
		#print(state[self.var])
		return state[self.var]

class StringExp(Expression):
	def __init__(self, s):
		self.var= s.strip("\"")

	def eval(self,state):
		#print(state[self.var])
		return self.var

class PlusExp(Expression):
	def __init__(self, s):
		l,r=s.split("+")
		self.l=Expression.build(l)
		self.r=Expression.build(r)

	def eval(self,state):
		return self.l.eval(state)+self.r.eval(state)

class SubExp(Expression):
	def __init__(self, s):
		l,r=s.split("-")
		self.l=Expression.build(l)
		self.r=Expression.build(r)

	def eval(self,state):
		return self.l.eval(state)-self.r.eval(state)

class MulExp(Expression):
	def __init__(self, s):
		l,r=s.split("*")
		self.l=Expression.build(l)
		self.r=Expression.build(r)

	def eval(self,state):
		return self.l.eval(state)*self.r.eval(state)

class DivExp(Expression):
	def __init__(self, s):
		l,r=s.split("/")
		self.l=Expression.build(l)
		self.r=Expression.build(r)

	def eval(self,state):
		return self.l.eval(state)/self.r.eval(state)


if __name__=='__main__':
	toycode=sys.argv[1]
	file=open(toycode)
	characters=file.read()
	file.close()
	a={}
	a=characters.strip().split("\n")
	a=list(filter(None, a))
	#print(a)
p=program(a)
state={}
p.eval(state)
#print(state)
		
		
	