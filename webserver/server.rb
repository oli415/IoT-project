require 'sinatra/base'
require 'sinatra-websocket'

#set :server, 'thin'
#set :sockets, []

Choices = {
  'ON' => 'Turn LED ON',
  'OFF' => 'Turn LED OFF',
}

class MyApp < Sinatra::Base
  set :bin, '0.0.0.0'
  set :environment, :production

  get "/" do
    @title = "Welcome to the Sato Lab IoT Project Web Interface!"
    erb :index
  end

  post "/actuate" do
    erb :index
  end

  run! if app_file == $0
end
