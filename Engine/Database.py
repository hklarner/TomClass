import sqlite3
import sys
import os

from Engine import Models
reload(Models)

EXMANY_LIMIT = 1000
SQLITE_KEYWORDS = ['ABORT', 'ACTION', 'ADD', 'AFTER', 'ALL', 'ALTER', 'ANALYZE', 'AND', 'AS', 'ASC', 'ATTACH', 'AUTOINCREMENT', 'BEFORE', 'BEGIN', 'BETWEEN', 'BY', 'CASCADE', 'CASE', 'CAST', 'CHECK', 'COLLATE', 'COLUMN', 'COMMIT', 'CONFLICT', 'CONSTRAINT', 'CREATE', 'CROSS', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'DATABASE', 'DEFAULT', 'DEFERRABLE', 'DEFERRED', 'DELETE', 'DESC', 'DETACH', 'DISTINCT', 'DROP', 'EACH', 'ELSE', 'END', 'ESCAPE', 'EXCEPT', 'EXCLUSIVE', 'EXISTS', 'EXPLAIN', 'FAIL', 'FOR', 'FOREIGN', 'FROM', 'FULL', 'GLOB', 'GROUP', 'HAVING', 'IF', 'IGNORE', 'IMMEDIATE', 'IN', 'INDEX', 'INDEXED', 'INITIALLY', 'INNER', 'INSERT', 'INSTEAD', 'INTERSECT', 'INTO', 'IS', 'ISNULL', 'JOIN', 'KEY', 'LEFT', 'LIKE', 'LIMIT', 'MATCH', 'NATURAL', 'NO', 'NOT', 'NOTNULL', 'NULL', 'OF', 'OFFSET', 'ON', 'OR', 'ORDER', 'OUTER', 'PLAN', 'PRAGMA', 'PRIMARY', 'QUERY', 'RAISE', 'REFERENCES', 'REGEXP', 'REINDEX', 'RELEASE', 'RENAME', 'REPLACE', 'RESTRICT', 'RIGHT', 'ROLLBACK', 'ROW', 'SAVEPOINT', 'SELECT', 'SET', 'TABLE', 'TEMP', 'TEMPORARY', 'THEN', 'TO', 'TRANSACTION', 'TRIGGER', 'UNION', 'UNIQUE', 'UPDATE', 'USING', 'VACUUM', 'VALUES', 'VIEW', 'VIRTUAL', 'WHEN', 'WHERE']

def New(Name, Model):
    if not '.' in Name:
        Name += '.sqlite'

    con = sqlite3.connect(Name)
    cur = con.cursor()

    header = ', '.join(['%s INT'%p for p in Model.parameters])
    unique = ', '.join([str(p) for p in Model.parameters])

    sql = 'CREATE TABLE Parametrizations('+header+', UNIQUE('+unique+') ON CONFLICT IGNORE)'
    cur.execute(sql)

    sql = 'CREATE TABLE Regulations( Regulator TEXT, Target TEXT, Thresholds TEXT )'
    cur.execute(sql)

    sql = 'INSERT INTO Regulations (Regulator, Target, Thresholds) VALUES (?,?,?)'
    stack = []
    for comp in Model.components:
        for target, thrs in comp.targets:
            stack.append((comp.name, target.name, ','.join([str(i) for i in thrs])))
    cur.executemany(sql, stack)

    sql = 'CREATE TABLE Components (Name TEXT, MaxActivity INT)'
    cur.execute(sql)

    sql = 'INSERT INTO Components (Name, MaxActivity) VALUES (?,?)'
    stack = []
    for comp in Model.components:
        stack.append((comp.name, str(comp.max)))
    cur.executemany(sql, stack)

    sql = 'CREATE TABLE Annotations (Name TEXT, Description TEXT)'
    cur.execute(sql)

    con.commit()
    con.close()



class Interface(object):
    def __init__(self, Name):
        if not '.' in Name:
            Name+='.sqlite'

        if not os.path.isfile(Name):
            print Name,'does not exist, please create DB first.'
            raise Exception('Database does not exist')

        self.fname              = Name
        self.con                = sqlite3.connect(Name)
        self.con.row_factory    = sqlite3.Row
        self.con.text_factory   = str
        self.cur                = self.con.cursor()
        self.model              = self.get_model()

        column_names    = set([col['name'] for col in self.cur.execute('PRAGMA Table_Info(Parametrizations)')])
        parameter_names = set([p.name for p in self.model.parameters])
        property_names  = set([row['Name'] for row in self.cur.execute('SELECT Name FROM Annotations')])


        if column_names != set([]).union( parameter_names, property_names) :
            print ' **critical database error: columns in table parametrizations is not the union of parameter names and annotations:'
            print ' column_names:   ',     column_names
            print ' parameter_names:',  parameter_names
            print ' property_names: ',   property_names
            raise Exception

        self.parameter_names    = parameter_names
        self.column_names       = column_names
        self.property_names     = property_names

        sql = 'SELECT count(rowid) FROM Parametrizations'
        self.cur.execute(sql)
        row = self.cur.fetchone()
        self.size = row['count(rowid)']

        self.insert_stacks      = {}
        self.annotation_stacks  = {}

    def get_model(self):
        self.cur.execute('SELECT * FROM Regulations')
        interactions = [(a,b,  tuple([int(i) for i in str(thrs).split(',')])  ) for a,b,thrs in self.cur]

        self.cur.execute('SELECT * FROM Components')
        names = [(a,int(m)) for a,m in self.cur]

        return Models.Interface(names, interactions)

    def add_column(self, Name, Type, Description='' ):
        if Name in self.parameter_names or Name.upper() in SQLITE_KEYWORDS:
            print 'Choose another column name, "%s" is a reserved keyword.'%s
            raise Exception

        sql = 'ALTER TABLE Parametrizations ADD COLUMN %s %s'%(Name, Type)
        self.cur.execute(sql)
        sql = 'INSERT INTO Annotations (Name, Description) VALUES (?,?)'
        self.cur.executemany(sql, [(Name,Description)])
        self.con.commit()

    def reset_column(self, Name):
        sql = 'UPDATE Parametrizations SET %s=NULL'%Name
        self.cur.execute(sql)
        sql = 'UPDATE Annotations SET Description=NULL WHERE Name="%s"'%Name
        self.cur.execute(sql)
        self.con.commit()

    def delete_column(self, Name ):
        pass

    def info(self):
        pass

    def insert_row(self, Parameters, Labels={}):
        Id = tuple(sorted(Labels.items()))

        if not self.insert_stacks.has_key(Id):
            self.insert_stacks[Id]=[Parameters]
        else:
            self.insert_stacks[Id].append( Parameters )

            if len(self.insert_stacks[Id])>EXMANY_LIMIT:
                self._commit_inserts()

    def _commit_inserts(self):

        for Id in self.insert_stacks:
            p = [str(p) for p in self.model.parameters]
            properties = [prop for prop,label in Id]
            pstr = ', '.join(p+properties)
            qstr = ', '.join((len(p+properties))*'?')
            sql = 'INSERT INTO Parametrizations ('+pstr+') VALUES('+qstr+')'

            labels = [label for prop,label in Id]
            values = []
            for P in self.insert_stacks[Id]:
                values.append([str(P[p]) for p in self.model.parameters]+labels)

            self.cur.executemany(sql, values)
            self.con.commit()

        self.insert_stacks = {}

    def get_row(self, SQLSelection):
        sql = 'SELECT Rowid,* FROM Parametrizations WHERE '+SQLSelection+' LIMIT 1'
        self.cur.execute(sql)
        row = self.cur.fetchone()

        if row:
            params = {}
            for p in self.model.parameters:
                params[p] = row[p.name]
            labels = {}
            for p in self.property_names:
                labels[p] = row[p]

            return params, labels, row['rowid']
        return None,None,None

    def set_labels(self, SQLSelection, Values):
        setter      = ','.join([ '%s=%s'%item for item in sorted(Values.items())])
        sql = 'UPDATE Parametrizations SET %s WHERE %s'%(setter, SQLSelection)
        self.cur.execute(sql)
        self.con.commit()

    def _commit_updates(self):
        pass

    def count(self, SQL):
        if not SQL: return self.size

        sql = 'SELECT Count(rowid) FROM Parametrizations WHERE '+SQL
        self.cur.execute(sql)
        row = self.cur.fetchone()
        return row['Count(rowid)']

    def get_property_labels(self, Properties, SQLSelection=''):
        labels = {}
        for p in Properties:
            if p in self.property_names:
                sql = 'SELECT DISTINCT '+p+' FROM Parametrizations'
                if SQLSelection:
                    sql+= ' WHERE '+SQLSelection

                self.cur.execute(sql)
                labels[p] = []
                for row in self.cur:
                    labels[p].append(row[p])

        return labels

    def close(self):
        self.con.commit()
        self._commit_inserts()
        self._commit_updates()
        self.con.close()
