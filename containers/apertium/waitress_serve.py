from waitress import serve
import appertium_server


serve(appertium_server.app, host='0.0.0.0', port=8005)
