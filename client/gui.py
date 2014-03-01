from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import string,cgi,time, json, random, copy, pickle, image64, os, exchange
import pybitcointools as pt

PORT=8090
def fs2dic(fs):
    dic={}
    for i in fs.keys():
        a=fs.getlist(i)
        if len(a)>0:
            dic[i]=fs.getlist(i)[0]
        else:
            dic[i]=""
    return dic
form='''
<form name="first" action="{}" method="{}">
<input type="submit" value="{}">{}
</form> {}
'''
def easyForm(link, button_says, moreHtml='', typee='post'):
    a=form.format(link, '{}', button_says, moreHtml, "{}")
    if typee=='get':
        return a.format('get', '{}')
    else:
        return a.format('post', '{}')
linkHome = easyForm('/', 'HOME', '', 'get')
def page1(dic):
#    privkey=pt.sha256("Brain Wallet3 ")
    return empty_page.format(easyForm('/info', 'Brain Wallet', '<input type="text" value="Brain Wallet (change this)"><input type="hidden" name="brain_wallet" value="Brain Wallet">'))
def info(dic):
    if 'brain_wallet' in dic:
        privkey=pt.sha256(dic['brain_wallet'])
    else:
        privkey=dic['privkey']
    print('privkey: ' +str(privkey))
    user=pt.privtopub(privkey)
    if 'command' in dic:
        if dic['command']=='sell_bid':
            exchange.sell_bid(user, privkey, dic['bid_id'])
        if dic['command']=='buy_bid':
            exchange.buy_bid(user, privkey, dic['buy_currency'], dic['buy_amount'], dic['sell_currency'], dic['sell_amount'])
    out=empty_page
    a=''
    while a=='':
        a=exchange.user_data(user, privkey)
    print('a: ' +str(a))
    out=out.format('your user name: '+str(a['user'])+'<br>{}')
    out=out.format('bitcoin deposit address: '+str(exchange.deposit_address(user, privkey, 'bitcoin')['deposit_address'])+'<br>{}')
    if a['bitcoin'] != a['bitcoin_unconfirmed']:
        string=str(a['bitcoin'])+'/'+str(a['bitcoin_unconfirmed'])
    else:
        string=str(a['bitcoin'])
    out=out.format('bitcoin balance: '+string+'<br>{}')
    if a['bitcoin']>0:
        out=out.format(easyForm('/info', 'buy litecoin', '\
<input type="hidden" name="privkey" value="'+privkey+'">\
<input type="hidden" name="command" value="buy_bid">\
<input type="hidden" name="buy_currency" value="litecoin">\
<input type="hidden" name="sell_currency" value="bitcoin">\
<input type="text" name="buy_amount" value="buy this much litecoin">\
<input type="text" name="sell_amount" value="sell this much bitcoin">\
'))
        out=out.format(easyForm('/info', 'withdraw bitcoin', '\
<input type="hidden" name="privkey" value="'+privkey+'">\
<input type="hidden" name="command" value="withdraw">\
<input type="hidden" name="currency" value="bitcoin">\
<input type="text" name="to_address" value="to address">\
<input type="text" name="amount" value="amount">\
'))
    out=out.format('litecoin deposit address: '+str(exchange.deposit_address(user, privkey, 'litecoin')['deposit_address'])+'<br>{}')
    if a['litecoin'] != a['litecoin_unconfirmed']:
        string=str(a['litecoin'])+'/'+str(a['litecoin_unconfirmed'])
    else:
        string=str(a['litecoin'])
    try:
        out=out.format('litecoin balance: '+string+'<br>{}')
    except:
        print('string: ' +str(string))
        print('out: '+str(out))
        error('here')
    if a['litecoin']>0:
        out=out.format(easyForm('/info', 'buy bitcoin', '\
<input type="hidden" name="privkey" value="'+privkey+'">\
<input type="hidden" name="command" value="buy_bid">\
<input type="hidden" name="buy_currency" value="bitcoin">\
<input type="hidden" name="sell_currency" value="litecoin">\
<input type="text" name="buy_amount" value="buy this much bitcoin">\
<input type="text" name="sell_amount" value="sell this much litecoin">\
'))
        out=out.format(easyForm('/info', 'withdraw litecoin', '\
<input type="hidden" name="privkey" value="'+privkey+'">\
<input type="hidden" name="command" value="withdraw">\
<input type="hidden" name="currency" value="litecoin">\
<input type="text" name="to_address" value="address to send to">\
<input type="text" name="amount" value="how much you want to send">\
'))
    out=out.format('<br>{}')
    if 'bids' in a:
        for i in a['bids']:
            out=out.format('bid_id: '+i['bid_id']+'<br>{}')
            out=out.format(easyForm('/info', 'undo bid and reclaim money', '<input type="hidden" name="command" value="sell_bid"><input type="hidden" name="bid_id" value="'+i['bid_id']+'"><input type="hidden" name="privkey" value="'+privkey+'">'))
            out=out.format('buy '+str(i['buy_amount'])+' of '+str(i['buy_currency'])+'<br>{}')
            out=out.format('sell '+str(i['sell_amount'])+' of '+str(i['sell_currency'])+'<br><br>{}')
    return out.format('')
def hex2htmlPicture(string):
    return '<img height="{}" src="data:image/png;base64,{}">{}'.format(str(picture_height), string, '{}')
def file2hexPicture(fil):
    return image64.convert(fil)
def file2htmlPicture(fil):
    return hex2htmlPicture(file2hexPicture(fil))
def newline():
    return '''<br />
{}'''
empty_page='<html><body>{}</body></html>'
initial_db={}
database='tags.db'
def fs_load():
    try:
        out=pickle.load(open(database, 'rb'))
        return out
    except:
        fs_save(initial_db)
        return pickle.load(open(database, 'rb'))      
def fs_save(dic):
    pickle.dump(dic, open(database, 'wb'))
class MyHandler(BaseHTTPRequestHandler):
   def do_GET(self):
      try:
         if self.path == '/' :    
#            page = make_index( '.' )
            self.send_response(200)
            self.send_header('Content-type',    'text/html')
            self.end_headers()
            self.wfile.write(page1({}))
            return    
         else : # default: just send the file    
            filepath = self.path[1:] # remove leading '/'    
            if [].count(filepath)>0:
#               f = open( os.path.join(CWD, filepath), 'rb' )
                 #note that this potentially makes every file on your computer readable bny the internet
               self.send_response(200)
               self.send_header('Content-type',    'application/octet-stream')
               self.end_headers()
               self.wfile.write(f.read())
               f.close()
            else:
               self.send_response(200)
               self.send_header('Content-type',    'text/html')
               self.end_headers()
               self.wfile.write("<h5>Don't do that</h5>")
            return
         return # be sure not to fall into "except:" clause ?      
      except IOError as e :  
             # debug    
         print e
         self.send_error(404,'File Not Found: %s' % self.path)
   def do_POST(self):
            print("path: " + str(self.path))
#         try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))    
            print(ctype)
            if ctype == 'multipart/form-data' or ctype=='application/x-www-form-urlencoded':    
               fs = cgi.FieldStorage( fp = self.rfile,
                                      headers = self.headers, # headers_,
                                      environ={ 'REQUEST_METHOD':'POST' })
            else: raise Exception("Unexpected POST request")
            self.send_response(200)
            self.end_headers()
            dic=fs2dic(fs)
            
            if self.path=='/info':
                self.wfile.write(info(dic))
            else:
                print('ERROR: path {} is not programmed'.format(str(self.path)))
def main():
   try:
      server = HTTPServer(('', PORT), MyHandler)
      print 'started httpserver...'
      server.serve_forever()
   except KeyboardInterrupt:
      print '^C received, shutting down server'
      server.socket.close()
if __name__ == '__main__':
   main()




