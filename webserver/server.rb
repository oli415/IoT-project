require 'sinatra/base'
require 'sinatra-websocket'
require 'json'

Choices = {
  'ON' => 'Turn LED ON',
  'OFF' => 'Turn LED OFF',
}

def is_json?(json)
  begin
    JSON.parse(json)
    return true
  rescue Exception => e
    return false
  end
end

class MyApp < Sinatra::Base
  set :server, 'thin'
  set :sockets, []

  set :bin, '0.0.0.0'
  set :environment, :production

  @@gateway_connected = 0 #class variable
  @msg_content = "" #instance variable

  get '/' do
    if !request.websocket?
      @title = 'Welcome to the Sato Lab IoT Project Web Interface!'
      if @@gateway_connected == 0
        erb :index
      else #gateway is connected -> serve the Control Interface
        erb :connected
      end
    else
      @@gateway_connected = 1
      request.websocket do |ws|
        ws.onopen do
          ws.send("Hello World!")
          settings.sockets << ws           
        end
        ws.onmessage do |msg|
          #EM.next_tick { settings.sockets.each{|s| s.send(msg) } } #echo message
          #check if the message has a known format and pass it to javascript
          if is_json?(msg) == true
            msg_json = JSON.parse(msg)
            if (msg_json.key?("T") && msg_json.key?("H") && msg_json.key?("t"))
              @msg_content = msg_json
            end
          else
            puts "No valid JSON"
          end
        end
        ws.onclose do
          @@gateway_connected = 0
          warn("websocket closed")
          settings.sockets.delete(ws)
        end
      end
    end
  end
  
  post '/actuate' do
    @title = 'Welcome to the Sato Lab IoT Project Web Interface!'
    @act = params['act']
    settings.sockets.each{ |s|
      s.send("LED = " + @act) } #send command to turn on or off LED
    erb :connected
  end

  run! if app_file == $0
end
