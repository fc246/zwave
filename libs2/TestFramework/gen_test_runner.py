#!/usr/bin/python

# Copyright (c) 2018 Silicon Laboratories Inc.

import sys
import os
import re
from io import open

n=0
regexp = '^void (test_[A-Za-z0-9_]+)\(.*\).*'

filename, file_type = os.path.splitext(sys.argv[1])

funcs = []

for l in open(sys.argv[1], encoding='utf-8'):
    m = re.search(regexp, l)
    if(m):
        funcs.append( (m.group(1).strip(),n) )
    n=n+1

print(''' 
/* AUTOGENERATED FILE. DO NOT EDIT. */
''')

if(file_type == '.cpp'):
    print('''
extern "C" {
''')

print('''
  #include "unity.h"
  #include "unity_print.h"
  #include "unity_internals.h"
#ifndef __codasip__
  #include "string.h"
#endif /* __codasip__ */
''')

if(file_type == '.cpp'):
    print('''
}
''')

print('''
int verbose;
''')

for f in funcs:
    print("void {}();".format(f[0]))

print('''

// Inspired by how Unity creates the setUp and tearDown functions
// Purpose is a setup and teardown method called before suite is run,
// and after suite is run.
#if defined(UNITY_WEAK_ATTRIBUTE)
    void setUpSuite(void);
    void tearDownSuite(void);
    UNITY_WEAK_ATTRIBUTE void setUpSuite(void) { }
    UNITY_WEAK_ATTRIBUTE void tearDownSuite(void) { }
#elif defined(UNITY_WEAK_PRAGMA)
#   pragma weak setUpSuite
    void setUpSuite(void);
#   pragma weak tearDownSuite
    void tearDownSuite(void);
#else
    void setUpSuite(void);
    void tearDownSuite(void);
#endif
''')

print('''

#ifdef __C51__
#include "reg51.h"

void setUp() {
#if 1
SCON  = 0x50;                   /* SCON: mode 1, 8-bit UART, enable rcvr    */
TMOD |= 0x20;                   /* TMOD: timer 1, mode 2, 8-bit reload      */
TH1   = 0xf3;                   /* TH1:  reload value for 2400 baud         */
TR1   = 1;                      /* TR1:  timer 1 run                        */
TI    = 1;                      /* TI:   set TI to send first char of UART  */
#else
  int bBaudRate;
  WATCHDOG_DISABLE;
  bBaudRate = 1152;
  bBaudRate = (80000/bBaudRate ) + (((80000 %bBaudRate ) >= (bBaudRate >> 1))  ? 1:0);
  UART0_SET_BAUD_RATE(68);
  UART0_TX_ENABLE;
  
  OPEN_IOS
  UART0BUF = '*';
#endif

}

void tearDown() {

}

extern int main(void) {
    int i;
    int ret;

    setUpSuite();
    verbose=0;
    unity_print_init();
    UNITY_BEGIN();

''')
for f in funcs:
    print('    UnityDefaultTestRun(&{}, "{}", {});'.format(f[0], f[0], f[1]))
print('''
    ret = UNITY_END();
    unity_print_close();
    tearDownSuite();
    while(1);
}
#else
int main(int argc, char** argp) {
    int ret;
    setUpSuite();
    unity_print_init();
    UNITY_BEGIN();


    if(argc==2) {
      verbose=1;
''')
for f in funcs:
    print(' if(strcmp(argp[1],"{}") == 0)   UnityDefaultTestRun(&{}, "{}", {});'.format(f[0], f[0], f[0], f[1]))
print('''
    } else {

''')
for f in funcs:
    print('    UnityDefaultTestRun(&{}, "{}", {});'.format(f[0], f[0], f[1]))
print('''
    }

    ret = UNITY_END();
    unity_print_close();
    tearDownSuite();
    return ret;
}
#endif

''')
