from random import random as rd
from math import *

#___UNIFORME___
def uniforme_continua(a,b):
    return a+(b-a)*rd()

def uniforme_discreta(a,b):
    return int(a+(b+1-a)*rd())

#___BERNOULLI___
def bernoulli(p,v1,v2):
    if rd()<p:
        return v1
    return v2

#___BINOMIAL___
def binomial(n,w):
    x = 0
    for i in range(n):
        if rd()<=w:
            x = x+1
    return x

#___POISSON___
def poisson(h):
    y = rd()
    k = 0
    u = 1
    v = 1
    while v<y*exp(h):
        k = k+1
        u = u*h/k
        v = v+u
    return k

#___NORMAL___
def normal_sin(m,s):
    y1 = rd()
    y2 = rd()
    t = sqrt(-2*log(y1))*sin(2*pi*y2)
    return m+s*t

def normal_sin_truncada(m,s,a,b):
    x = normal_sin(m,s)
    while not a<x<b:
        x = normal_sin(m,s)
    return x

def normal_cos(m,s):
    y1 = rd()
    y2 = rd()
    t = sqrt(-2*log(y1))*cos(2*pi*y2)
    return m+s*t

def normal_cos_truncada(m,s,a,b):
    x = normal_cos(m,s)
    while not a<x<b:
        x = normal_cos(m,s)
    return x

#___TRIANGULAR___
def triangular_x(x,a,b,c):
        if x<c:
            return (2*(x-a))/((b-a)*(c-a))
        return (2*(b-x))/((b-a)*(b-c))
            
def triangular(a,b,c):
    h = 2/(b-a)
    z = a+(b-a)*rd()
    while not rd() <= triangular_x(z,a,b,c)/h:
        z = a+(b-a)*rd()
    return z

#___EXPONENCIAL___
def exponencial(h):
    return -1/h * log(rd())

#___ERLANG-K___
def erlang(k,m):
    p = 1
    for i in range(k):
        p = p*rd()
    return -m/k*log(p)