# -*- coding: utf-8 -*-
import pygame
import sys
from pygame.locals import QUIT,KEYDOWN,K_LEFT,K_a,K_UP,K_w,K_RIGHT,K_d,K_DOWN,K_s,K_ESCAPE,K_r
from os.path import abspath,join
from random import choice,randint as random
from time import sleep
import pickle
from itertools import count
import numpy as np

LINE_LENGTH=4

IMAGE_NUMBER=13

class LastStepException(Exception):
    pass
class QuitException(Exception):
    pass
class GetBackException(Exception):
    pass


class _loadsave(object):
    @classmethod
    def load(cls):
        try:
            with open(cls.filename,'rb') as file:
                return pickle.load(file)
        except:
            return cls.new()
    
    def save(self):
        with open(self.filename,'wb') as file:
            pickle.dump(self,file)

##### - - - - - score - - - - - #####

class point(_loadsave):
    filename='point.sxm'
    class _subtype():
        def __init__(self):
            self.actual=0
            self.highest=0
        def __getstate__(self):
            return self.actual,self.highest
        def __setstate__(self,state):
            self.actual=state[0]
            self.highest=state[1]
    @classmethod
    def new(cls):
        print('new')
        self=object.__new__(cls)
        self._data={LINE_LENGTH:cls._subtype()}
        return self
    
    def __init__(self):
        self._data={LINE_LENGTH:self._subtype()}

    def __getstate__(self):
        return self._data
    def __setstate__(self,state):
        self._data=state
        
    def get_actual(self):
        try:
            return self._data[LINE_LENGTH].actual
        except KeyError:
            self._data={LINE_LENGTH:self._subtype()}
            return 0
    def set_actual(self,value):
        try:
            obj=self._data[LINE_LENGTH]
        except KeyError:
            obj=self._subtype()
            self._data[LINE_LENGTH]=obj
        obj.actual=value
        if value>obj.highest:
            obj.highest=value
        self.save()
    def del_actual(self):
        try:
            self._data[LINE_LENGTH].actual=0
        except KeyError:
            self._data={LINE_LENGTH:self._subtype()}
        self.save()
    def get_highest(self):
        try:
            return self._data[LINE_LENGTH].highest
        except KeyError:
            self._data={LINE_LENGTH:self._subtype()}
            return 0
    
    actual=property(get_actual,set_actual,del_actual)
    highest=property(get_highest,None,None)
    del get_actual,set_actual,del_actual,get_highest
    
##### - - - - - pygame - - - - - #####
    
pygame.init()

FONT_GENERAL=pygame.font.Font(None,24)
FONT_BIG=pygame.font.SysFont("comicsansms",60)
FONT_COLOR=(0,0,0)

class score(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.update()
        self.rect=self.image.get_rect().move(x,y)
        
class score_actual(score):
    def update(self):
        self.image=FONT_GENERAL.render('Points: '+str(POINT.actual),0,FONT_COLOR)

        
class score_highest(score):
    def update(self):
        self.image=FONT_GENERAL.render('Highest: '+str(POINT.highest),0,FONT_COLOR)

class large_text(pygame.sprite.Sprite):
    def __init__(self,x,y,text):
        pygame.sprite.Sprite.__init__(self)
        self.image=FONT_BIG.render(text,0,FONT_COLOR)
        size=self.image.get_size()
        self.rect=self.image.get_rect().move(x-size[0]//2,y-size[1]//2)

class button(pygame.sprite.Sprite):
    _passive_color=(0,200,0)
    _active_color=(0,255,0)
    def __init__(self,coords,command):
        pygame.sprite.Sprite.__init__(self)
        self.x1=coords[0]
        self.y1=coords[1]
        self.x2=coords[2]
        self.y2=coords[3]
        self.state=False
        self.command=command
        self.image=pygame.Surface([coords[2]-coords[0],coords[3]-coords[1]])
        self.rect=self.image.get_rect().move(coords[0],coords[1])
        self.update()
    def update(self):
        mouse=pygame.mouse.get_pos()
        click=pygame.mouse.get_pressed()
        if self.x1<mouse[0]<self.x2 and self.y1<mouse[1]<self.y2:
            if self.state==False:
                self.image.fill(self._active_color)
                self.state=True
            if click[0]==1:
                self.command()
        else:
            if self.state==True:
                self.image.fill(self._active_color)
                self.state=False
            self.image.fill(self._passive_color)

class text_on_button(pygame.sprite.Sprite):
    def __init__(self,coords,text):
        pygame.sprite.Sprite.__init__(self)
        self.image=FONT_GENERAL.render(text,0,FONT_COLOR)
        size=self.image.get_size()
        self.rect=self.image.get_rect().move((coords[0]+coords[2]-size[0])//2,(coords[1]+coords[3]-size[1])//2)

##### - - - - - math - - - - - #####
def _it_con_builder(it,start,end):
    it=iter(it)
    _next=it.__next__
    try:
        v0=_next()
    except:
        yield start+end
        return
    try:
        v1=_next()
        yield start+str(v0)
    except:
        yield start+str(v0)+end
        return
    while True:
        try:
            v0=_next()
            yield str(v1)
        except:
            yield str(v1)+end
            return
        try:
            v1=_next()
            yield str(v0)
        except:
            yield str(v0)+end
            return
    
def it_con(it,sep=', ',start='[',end=']'):
    return sep.join(_it_con_builder(it,start,end))

class data_object():
    _aims=['left','top','right','bot']
    _aimln=len(_aims)
    def __init__(self,line_length,fill=0,aim='left'):
        self._buffer=np.full(line_length**2,fill,np.uint32)
        self._line_length=line_length
        self._size=line_length**2
        self.aim=aim
        
    def _get_aim(self):
        return self._aims[self._aim]
    def _set_aim(self,value):
        if isinstance(value,int):
            if -1<value<self._aimln:
                self._aim=value
            else:
                raise ValueError('Invalid aim, it can be only from 0, till '+str(self._aimln))
        elif isinstance(value,str):
            try:
                self._aim=self._aims.index(value)
            except ValueError as error:
                error.args=('Invalid aim, it can be only:'+','.join(self._aims))
                raise
        else:
            raise TypeError('aim\'s type can be only str or int')
    aim=property(_get_aim,_set_aim)
    del _get_aim,_set_aim

    @property
    def line_length(self):
        return self._line_length
    def __len__(self):
        return self._size
    def __repr__(self):
        return self._buffer.reshape((self._line_length,self._line_length),).__repr__()
    __str__=__repr__
    def __iter__(self):
        return _data_iterator(self)
    def __reversed__(self):
        return _data_reversed_iterator(self)
    def __getitem__(self,xy):
        return self._buffer[xy[0]+xy[1]*self.self._line_length]
    def __setitem__(self,xy,value):
        self._buffer[xy[0]+xy[1]*self._line_length]=value
        
    def __getstate__(self):
        return self._buffer,self._line_length,self._aim
    def __setstate__(self,state):
        self._buffer=state[0]
        self._line_length=state[1]
        self._aim=state[2]
        self._size=self._line_length**2
    
class _data_line_acces:
    def __init__(self,buffer,start,step,line_length):
        self._buffer=buffer
        self._start=start
        self._step=step
        self._line_length=line_length
    def __len__(self):
        return self._line_length
    def __getitem__(self,index):
        if index<0 or self._line_length<=index:
            raise IndexError
        return self._buffer[self._start+self._step*index]
    def __setitem__(self,index,value):
        if index<0 or self._line_length<=index:
            raise IndexError
        self._buffer[self._start+self._step*index]=value
    def __delitem__(self,index):
        if index<0 or self._line_length<=index:
            raise IndexError
        step=self._step
        index=self._start+step*index
        end=self._start+(self._line_length-1)*step
        buffer=self._buffer
        if step>0:
            while index<end:
                buffer[index]=buffer[index+step]
                index+=step
        else:
            while index>end:
                buffer[index]=buffer[index+step]
                index+=step
        buffer[index]=0
        self._line_length-=1
    def __repr__(self):
        return it_con(self)
    __str__=__repr__
    def __iter__(self):
        return _data_line_iterator(self)
    def __reversed__(self):
        return _data_line_reversed_iterator(self)
    def copy(self):
        return np.fromiter(self,np.uint32)
    def __eq__(self,other):
        ln_self=self._line_length
        ln_other=len(other)
        index=0
        if ln_self<ln_other:
            for index in range(ln_self):
                if self[index]!=other[index]:
                    return False
            for index in range(index+1,ln_other):
                if other[index]:
                    return False
        elif ln_self>ln_other:
            for index in range(ln_other):
                if self[index]!=other[index]:
                    return False
            for index in range(index+1,ln_self):
                if self[index]:
                    return False
        else:
            for index in range(ln_self):
                if self[index]!=other[index]:
                    return False
        return True
    def __ne__(self,other):
        ln_self=self._line_length
        ln_other=len(other)
        index=0
        if ln_self<ln_other:
            for index in range(ln_self):
                if self[index]!=other[index]:
                    return True
            for index in range(index+1,ln_other):
                if other[index]:
                    return True
        elif ln_self>ln_other:
            for index in range(ln_self):
                if self[index]!=other[index]:
                    return True
            for index in range(index+1,ln_self):
                if self[index]:
                    return True
        else:
            for index in range(ln_self):
                if self[index]!=other[index]:
                    return True
        return False
    
def _data_line_iterator(parent):
    buffer=parent._buffer
    for index in range(parent._start,parent._start+parent._step*parent._line_length,parent._step):
        yield buffer[index]
        
def _data_line_reversed_iterator(parent):
    buffer=parent._buffer
    for index in range(parent._start+parent._step*(parent._line_length-1),parent._start-parent._step,-parent._step):
        yield buffer[index]
    
def _data_iterator(parent):
    line_length=parent._line_length
    buffer=parent._buffer
    if parent._aim<2:
        if parent._aim==0:
            for index in range(0,parent._size,line_length):
                yield _data_line_acces(buffer,index,1,line_length)
        else:
            for index in range(0,line_length,1):
                yield _data_line_acces(buffer,index,line_length,line_length)
    else:
        if parent._aim==2:
            for index in range(line_length-1,parent._size,line_length):
                yield _data_line_acces(buffer,index,-1,line_length)
        else:
            for index in range(parent._size-line_length,parent._size,1):
                yield _data_line_acces(buffer,index,-line_length,line_length)

def _data_reversed_iterator(parent):
    line_length=parent._line_length
    buffer=parent._buffer
    if parent._aim<2:
        if parent._aim==0:
            for index in range(parent._size-line_length,-line_length,-line_length):
                yield _data_line_acces(buffer,index,1,line_length)
        else:
            for index in range(line_length-1,-1,-1):
                yield _data_line_acces(buffer,index,line_length,line_length)
    else:
        if parent._aim==2:
            for index in range(parent._size-1,-1,-line_length):
                yield _data_line_acces(buffer,index,-1,line_length)
        else:
            for index in range(parent._size-1,parent._size-line_length-1,-1):
                yield _data_line_acces(buffer,index,-line_length,line_length)  

##### - - - - - core - - - - - #####
    
class core(data_object,_loadsave):
    filename='save.sxm'
    @classmethod
    def new(cls):
        POINT.actual=0
        self=cls(LINE_LENGTH)
        self.create_random()
        self.create_random()
        self.save()
        return self
        
    def create_random(self):
        buffer=self._buffer
        counter=-1
        for element in buffer:
            if not element:
                counter+=1
        if counter<0:
            return
        counter=random(0,counter)
        for index in count():
            if not buffer[index]:
                if counter:
                    counter-=1
                else:
                    buffer[index]=random(4,8)>>2
                    break
    
    def push_lines(self):
        counter=self._line_length
        for line in self:
            linecopy=line.copy()
            for index,value in zip(reversed(range(self._line_length)),reversed(line)):
                if not value:
                    del line[index]
            try:
                for index in count():
                    if line[index]==line[index+1]:
                        POINT.actual+=1<<line[index]
                        line[index]+=1
                        del line[index+1]
            except IndexError:
                pass
            if line==linecopy:
                counter-=1
        return counter
    def move_test(self):
        buffer=self._buffer
        if 0 in buffer:
            return True
        line_length=self._line_length
        for start in range(0,self._size,line_length):
            for index in range(start,start+line_length-1):
                if buffer[index]==buffer[index+1]:
                    return True
        for start in range(line_length):
            for index in range(start,self._size-line_length,line_length):
                if buffer[index]==buffer[index+line_length]:
                    return True
        return False

    def screen_flip(self):
        images=self.images
        buffer=self._buffer
        it=range(self._line_length)
        for x in it:
            for y in it:
                SCREEN.blit(images[buffer[y*self._line_length+x]],(5+110*x,5+110*y))
        pygame.display.flip()

    def move(self,aim):
        if not self.move_test():
            raise LastStepException()
        self.aim=aim
        if self.push_lines():
            self.create_random()
            self.screen_flip()
            self.save()

##### - - - - - game - - - - - #####

class game():
    background_color=(239,228,176)
    def __init__(self,line_length=LINE_LENGTH):
        global SCREEN
        self._line_length=line_length
        v=line_length*110
        self.size=(v,v+25)
        SCREEN=pygame.display.set_mode(self.size)
        if not hasattr(core,'images'):
            path=join(abspath('.'),'data')+'\\%s.png'
            core.images=list(pygame.image.load(path%index).convert() for index in range(IMAGE_NUMBER))
        pygame.display.set_caption("DERP~2048")
    def gamescreen(self):
        global CORE
        background=pygame.Surface(self.size)
        background.fill(self.background_color)
        SCREEN.fill(self.background_color)
        pygame.display.flip()
        elements=pygame.sprite.RenderUpdates()
        score_actual.containers=elements
        elements.add(score_actual(15,self.size[1]-20))
        score_highest.containers=elements
        elements.add(score_highest(self.size[0]//2+15,self.size[1]-20))
        pygame.display.update(elements.draw(SCREEN))
        CORE.screen_flip()
        while 1:
            for event in pygame.event.get():
                if event.type==QUIT:
                    raise QuitException
                elif event.type==KEYDOWN:
                    key=event.key
                    try:
                        if key in (K_LEFT,K_a):
                            CORE.move(0)
                        elif key in (K_UP,K_w):
                            CORE.move(1)
                        elif key in (K_RIGHT,K_d):
                            CORE.move(2)
                        elif key in (K_DOWN,K_s):
                            CORE.move(3)
                        elif key==K_ESCAPE:
                            raise QuitException
                        elif key==K_r:
                            CORE=core.new()
                            CORE.screen_flip()
                    except QuitException:
                        raise
                    except LastStepException:
                        elements.empty()
                        raise LastStepException
                elements.clear(SCREEN,background)
                elements.update()
                pygame.display.update(elements.draw(SCREEN))
            sleep(0.05)
    
    def lostscreen(self):
        global SCREEN
        background_color=(239,228,176)
        background=pygame.Surface(self.size)
        background.fill(background_color)
        SCREEN.fill(background_color)
        pygame.display.update()
        pygame.display.flip()
        elements=pygame.sprite.RenderUpdates()
        large_text.containers=elements
        button.containers=elements
        text_on_button.containers=elements

        elements.add(large_text(self.size[0]//2,self.size[1]*2//5,'You lost, RIP'))
        
        def back():
            elements.empty()
            raise GetBackException

        y_start=self.size[1]*3//5
        y_end=y_start+50
        coords=[30,y_start,135,y_end]
        elements.add(button(coords,back))
        elements.add(text_on_button(coords,'Back'))

        def new_():
            global CORE
            elements.empty()
            CORE=core.new()
            raise GetBackException
        
        coords=[self.size[0]//2-52,y_start,self.size[0]//2+53,y_end]
        elements.add(button(coords,new_))
        elements.add(text_on_button(coords,'Try again'))

        def destroy():
            elements.empty()
            raise QuitException

        coords=[self.size[0]-135,y_start,self.size[0]-30,y_end]
        elements.add(button(coords,destroy))
        elements.add(text_on_button(coords,'Quit'))
        
        pygame.display.update(elements.draw(SCREEN))

        try:
            while 1:
                for event in pygame.event.get():
                    if event.type==QUIT:
                        raise QuitException
                
                elements.clear(SCREEN,background)
                elements.update()
                pygame.display.update(elements.draw(SCREEN))
                sleep(0.05)
        except GetBackException:
            pass

    def run(self):
        while True:
            try:
                try:
                    self.gamescreen()
                except LastStepException:
                    try:
                        self.lostscreen()
                    except GetBackException:
                        pass
            except QuitException:
                pygame.quit()
                sys.exit()

##### - - - - - starting - - - - - #####

POINT=point.load()

CORE=core.load()
if CORE.line_length!=LINE_LENGTH:
    CORE=core.new()

if __name__=='__main__':
    game().run()
