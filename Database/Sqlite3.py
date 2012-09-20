import sqlite3
import sys
import os

EXECUTE_MANY_SIZE = 400
SELECTION_COLUMN = 'Priority'


class Interface(object):
    def __init__(self, ProjectName, Model):
        self.parameters = sorted(Model.parameters)
        
        self.fname = os.path.join('Projects', ProjectName, ProjectName+'.db')
        if os.path.isfile(self.fname):
            print 'Connecting to',self.fname,'..',
            self.con = sqlite3.connect(self.fname)
            self.con.row_factory = sqlite3.Row
            self.cur = self.con.cursor()
            print 'ok'
            print 'Counting parametrizations:',
            self.cur.execute('SELECT COUNT(*) FROM Parametrizations')
            print self.cur.fetchone()[0]
        else:
            print 'Creating',self.fname,'..',
            self.con = sqlite3.connect(self.fname)
            self.cur = self.con.cursor()
            self.cur.execute('CREATE TABLE Parametrizations('+', '.join(['%s INT'%p for p in self.parameters])+')')
            self.cur.execute('ALTER TABLE Parametrizations ADD COLUMN %s INT'%SELECTION_COLUMN)
            print 'ok'
        
        self.insert_stack = []
        p_str = ', '.join([str(p) for p in self.parameters])
        q_str = ', '.join('?'*len(self.parameters))
        self.insert_str = 'INSERT INTO Parametrizations (%s) VALUES(%s)'%(p_str, q_str)

    def insert_parametrization(self, ParamDict):
        params = tuple([ParamDict[p] for p in self.parameters])
        self.insert_stack.append(params)
        if len(self.insert_stack) > EXECUTE_MANY_SIZE:
            self.cur.executemany(self.insert_str, self.insert_stack)
            self.insert_stack = []

    def register_classifier(self, Classifier):
        print 'Registering classifier..',
        
        self.classifier = Classifier
        forbidden = [str(p) for p in self.parameters] + [SELECTION_COLUMN]
        if Classifier.property_name in forbidden:
            print 'choose another property name,', Classifier.property_name, 'is a reserved keyword.'
            return False

        self.update_str = 'UPDATE Parametrizations SET %s=? WHERE Rowid=?'%Classifier.property_name
        
        for col in self.cur.execute('PRAGMA Table_Info(Parametrizations)'):
            if col['name'] == Classifier.property_name:
                if col['type'] == Classifier.property_type:
                    print 'property column exists.'
                    return True
                else:
                    print 'property column exists, but encountered type mismatch.'
                    return False
        
        print 'ok'
        print 'Creating property column..',
        self.cur.execute('ALTER TABLE Parametrizations ADD COLUMN %s %s'%(self.classifier.property_name, self.classifier.property_type))
        print 'ok'

    def is_finished(self):
        self.cur.execute('SELECT Rowid,* FROM Parametrizations WHERE %s=1 and %s IS NULL LIMIT 1'%(SELECTION_COLUMN, self.classifier.property_name))
        fetch = self.cur.fetchone()
        if fetch:
            return False
        return True

    def perform_classification(self, Iterations=1000):
        stack = []
        self.cur.execute('SELECT Rowid,* FROM Parametrizations WHERE %s=1 and %s IS NULL'%(SELECTION_COLUMN, self.classifier.property_name))

        count = 0
        for row in self.cur:
            if count>Iterations: break
            rowid= row['rowid']
            param= dict([(p,row[str(p)]) for p in self.parameters])
            count +=1
            label = self.classifier.compute_label(param)
            stack.append((label, rowid))
            
        self.cur.executemany(self.update_str, stack)
        self.con.commit()

        print '.',

    def set_selection(self, Selection):
        self.cur.execute('UPDATE Parametrizations SET %s=1 WHERE %s and %s IS NULL'%(SELECTION_COLUMN,Selection, self.classifier.property_name))
        self.con.commit()
        print 'Selected', self.cur.rowcount, 'parametrizations for classification.'

    def clear_selection(self):
        self.cur.execute('UPDATE Parametrizations SET %s=NULL WHERE %s IS NOT NULL'%(SELECTION_COLUMN,SELECTION_COLUMN))
        self.con.commit()
        print 'Cleared selection.'
        

    def close(self):
        if self.insert_stack:
            self.cur.executemany(self.insert_str, self.insert_stack)
            self.con.commit()
        print 'Closing connection to',self.fname,'..',
        self.con.close()
        print 'ok'
        
