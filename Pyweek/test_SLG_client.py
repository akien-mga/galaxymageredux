
import pygame
from pygame.locals import *
from lib import SLG, event, gui

class Engine(SLG.Client):
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((640,480))

        self.event_handler = event.Handler()


        ####GUI stuff!####

        lil_font = pygame.font.Font(None, 20)
        small_font = pygame.font.Font(None, 25)

        #pre connection login/etc.
        self.pre_conn_app = gui.App(self.screen, self.event_handler)
        x=gui.Label(self.pre_conn_app, (5,75), 'Connect to a server!')
        x.bg_color = (0,0,0,0)
        x.text_color = (255,255,255)

        cont = gui.Container(self.pre_conn_app, (300, 200), gui.RelativePos(to=x, pady=5))
        cont.bg_color = (100,100,255,100)
        cont.font = small_font

        x=gui.Label(cont, (5,5), 'Username:')
        x.bg_color = (0,0,0,0)
        x.text_color = (100,100,100)

        self.get_username = gui.Input(cont,
                                      210, gui.RelativePos(to=x, pady=5, padx=5),
                                      max_chars=20)
        self.get_username.always_active=False
        self.get_username.bg_color = (200,200,200)
        self.get_username.text_color = (100,100,100)

        x=gui.Label(cont, gui.RelativePos(to=self.get_username, pady=5, padx=-5), "Server:")
        x.bg_color = (0,0,0,0)
        x.text_color = (100,100,100)

        self.connect_server_drop = gui.DropDownMenu(cont, gui.RelativePos(to=x, pady=5, padx=5),
                                                    'main', ['main', 'local', 'other'])
        self.connect_server_drop.bg_color=(100,100,100)
        self.connect_server_serv = gui.Input(cont,
                                             200,
                                             gui.RelativePos(to=self.connect_server_drop, x='right', y='top',padx=5),
                                             -1)
        self.connect_server_serv.bg_color = (200,200,200)
        self.connect_server_serv.text_color = (100,100,100)
        self.connect_server_serv.always_active = False
        self.connect_server_serv.visible = False
        self.connect_server_serv.text = str(SLG.main_server_host)
        self.connect_server_drop.dispatch.bind('select', self.handle_server_sel)

        x=gui.Label(cont, gui.RelativePos(to=self.connect_server_drop, pady=5, padx=-5), "Port:")
        x.bg_color = (0,0,0,0)
        x.text_color = (100,100,100)

        self.connect_port_drop = gui.DropDownMenu(cont, gui.RelativePos(to=x, pady=5, padx=5),
                                                  'default', ['default', 'other'])
        self.connect_port_drop.bg_color = (100,100,100)
        self.connect_port_serv = gui.Input(cont,
                                             200,
                                             gui.RelativePos(to=self.connect_port_drop, x='right', y='top',padx=5),
                                             -1)
        self.connect_port_serv.bg_color = (200,200,200)
        self.connect_port_serv.text_color = (100,100,100)
        self.connect_port_serv.always_active = False
        self.connect_port_serv.visible = False
        self.connect_port_serv.text=str(SLG.main_server_port)
        self.connect_port_drop.dispatch.bind('select', self.handle_port_sel)

        self.connect_button = gui.Button(cont, gui.RelativePos(to=self.connect_port_drop, pady=5, padx=-5), 'Connect')
        self.connect_button.font = self.pre_conn_app.font
        self.connect_button.bg_color = (255,0,0)
        self.connect_button.text_hover_color = (100,100,100)
        self.connect_button.text_click_color = (200,200,200)

        self.get_username.dispatch.bind("input-submit", self.handle_connect)
        self.connect_button.dispatch.bind("click", self.handle_connect)
        popup = gui.PopUp(self.connect_button, text='Username must be between 4 and 20 characters long!')
        popup.bg_color = (255,255,255,100)
        #end pre conn

        #server lobby view
        self.server_lobby_app = gui.App(self.screen, self.event_handler)

        gamel = gui.Label(self.server_lobby_app, (5,75), 'Games:')
        gamel.text_color = (200,200,200)
        gamel.bg_color = (0,0,0,0)
        desc = gui.Label(self.server_lobby_app, gui.RelativePos(to=gamel), 'name <scenario> [master] (players / max) CAN JOIN')
        desc.text_color = (200,200,200)
        desc.bg_color = (0,0,0,0)
        desc.font = lil_font

        self.game_list_cont = gui.Container(self.server_lobby_app, (440, (lil_font.get_height()+2)*10), gui.RelativePos(to=desc,pady=5))
        self.game_list_cont.font = lil_font
        self.game_list_cont.bg_color = (200,100,100)

        self.game_list_select = gui.Menu(self.game_list_cont, (0,0), padding=(2,2))
        self.game_list_select.entry_bg_color = (200,75,75)
        self.game_list_select.dispatch.bind('select', self.handle_game_list_select)

        self.game_list_list = {}
        self.game_list_page = 0
        self.game_list_id = {}

        game_list_ppage = gui.Button(self.server_lobby_app, gui.RelativePos(to=self.game_list_cont, y='bottom', pady=5, padx=50), 'Last Page')
        game_list_ppage.dispatch.bind('click', lambda: self.view_game_page(self.game_list_page-1))

        self.game_list_lpage = gui.Label(self.server_lobby_app, gui.RelativePos(to=game_list_ppage, x='right', y='top', padx=5), 'Page: 0')

        game_list_npage = gui.Button(self.server_lobby_app, gui.RelativePos(to=self.game_list_lpage, x='right', y='top', padx=5), 'Next Page')
        game_list_npage.dispatch.bind('click', lambda: self.view_game_page(self.game_list_page+1))

        self.popup_bads_cont = gui.Container(self.server_lobby_app, (5,5), (0,0))
        self.popup_bads_cont.visible = False
        self.popup_bads_cont.bg_color = (255,255,255,175)
        popup_bads_label = gui.Label(self.popup_bads_cont, (5,15), "You don't have the required scenario to play this game!")
        popup_bads_label.bg_color=(0,0,0,0)
        popup_bads_label.font = lil_font
        w,h = popup_bads_label.get_size()
        self.popup_bads_cont.change_size((w+10, h+30))
        self.popup_bads_cont.dispatch.bind('unfocus', lambda:self.turn_off_widget(self.popup_bads_cont))

        self.server_lobby_messages = gui.MessageBox(self.server_lobby_app, (440, 100),
                                                    gui.RelativePos(to=game_list_ppage, pady=15, padx=-50))
        self.server_lobby_messages.bg_color = (200,75,75)
        self.server_lobby_messages.font = lil_font
        self.server_lobby_input = gui.Input(self.server_lobby_app, 350, gui.RelativePos(to=self.server_lobby_messages, pady=5),
                                            max_chars=30)
        self.server_lobby_input.bg_color = (200,75,75)
        self.server_lobby_input.text_color = (0,0,0)
        self.server_lobby_input.font = lil_font
        self.server_lobby_binput = gui.Button(self.server_lobby_app,
                                              gui.RelativePos(to=self.server_lobby_input, padx=5,x='right',y='top'),
                                              'Submit')
        self.server_lobby_binput.bg_color=(200,200,200)
        self.server_lobby_input.dispatch.bind('input-submit', self.lobby_submit_message)
        self.server_lobby_binput.dispatch.bind('click', self.lobby_submit_message)

        cont = gui.Container(self.server_lobby_app, (185, 470), (450, 5))
        cont.bg_color = (100,100,255,100)
        l = gui.Label(cont, (5, 5), 'Users in Lobby:')
        l.bg_color=(0,0,0,0)
        l.text_color=(100,100,100)

        self.server_lobby_users = gui.List(cont, gui.RelativePos(to=l, pady=5))
        self.server_lobby_users.font = lil_font
        self.server_lobby_users.entry_bg_color = (0,0,0,0)
        #end server lobby view


        #game room lobby view
        self.game_room_lobby = gui.App(self.screen, self.event_handler)


        self.pre_conn_app.activate()
        ###END GUI STUFF###


        ####Game controls####
        self.playing = False
        self.cur_game = None #this will hold a game engine class that stores all info about game! Kinda like a database

        self.scenario_list = ['test']
        ####End game controls####

        #start the game loop!
        SLG.Client.__init__(self, "changeme", SLG.main_server_host, SLG.main_server_port)


    ####Core net functions####
    def handle_connect(self, *args, **kwargs):
        text = self.get_username.text

        if len(text)>=4:
            self.username = text
            self.connect()

    def connected(self, avatar):
        SLG.Client.connected(self, avatar)
        self.server_lobby_app.activate()
        self.avatar.callRemote('getGameList')

    def disconnected(self):
        self.pre_conn_app.activate()
##        self.close()

    def remote_getMessage(self, player, message):
        if self.playing:
            pass #for in-game chats
        else:
            self.server_lobby_messages.add_line('%s: %s'%(player, message))

    ####End core net functions


    ###Pre conn gui functions
    def set_default_input(self, widg, inp):
        widg.text = inp
        widg.cursor_pos = len(inp)
    def handle_server_sel(self, value):
        if value == 'main':
            self.connect_server_serv.text = SLG.main_server_host
            self.connect_server_serv.visible = False
        elif value == 'local':
            self.connect_server_serv.text = 'localhost'
            self.connect_server_serv.visible = False
        elif value == 'other':
            self.connect_server_serv.text = SLG.main_server_host
            self.connect_server_serv.visible = True
            self.connect_server_serv.cursor_pos = len(SLG.main_server_host)
        self.connect_server_drop.text = value
    def handle_port_sel(self, value):
        if value == 'default':
            self.connect_port_serv.text = str(SLG.main_server_port)
            self.connect_port_serv.visible = False
        elif value == 'other':
            self.connect_port_serv.text = str(SLG.main_server_port)
            self.connect_port_serv.visible = True
            self.connect_port_serv.cursor_pos = len(SLG.main_server_host)
        self.connect_port_drop.text = value
    ###End pre conn functions


    #game lobby view functions#
    def lobby_submit_message(self, *args):
        message = self.server_lobby_input.text
        if message:
            self.avatar.callRemote('sendMessage', message)
            self.server_lobby_input.text = ''
            self.server_lobby_input.cursor_pos = 0
    def turn_off_widget(self, widg):
        widg.visible = False
    def turn_on_widget(self, widg):
        widg.visible = True

    def handle_game_list_select(self, value):
        game = self.game_list_list[value]
        game_id, name, scenario, master, players, max_players, in_game = game

        if not scenario in self.scenario_list:
            self.turn_on_widget(self.popup_bads_cont)
            self.popup_bads_cont.pos.x = 10
            self.popup_bads_cont.pos.y = pygame.mouse.get_pos()[1]
            self.popup_bads_cont.focus()
        else:
            print value

    def view_game_page(self, num):
        if num < 0:
            num = 0
        if num > len(self.game_list_list.values())*0.1:
            num = int(len(self.game_list_list.values())*0.1)

        self.game_list_page = num
        opts = []
        for game in sorted(self.game_list_list.values())[num*10:(num+1)*10]:
            game_id, name, scenario, master, players, max_players, in_game = game
            l = str(name) + ' <' + str(scenario) + '> ' + '[' + str(master) + '] '
            l += '(' + str(players) + ' / ' + str(max_players) + ')'
            if in_game:
                l+= ' -- CLOSED'
            else:
                l+= ' -- OPEN'
            opts.append(l)

        self.game_list_select.options = opts
        self.game_list_select.build_options()
        self.game_list_lpage.text = 'Page: %s'%num

    def remote_sendGameList(self, games):
        self.game_list_list = {}
        for game in games:
            game_id, name, scenario, master, players, max_players, in_game = game
            l = str(name) + ' <' + str(scenario) + '> ' + '[' + str(master) + '] '
            l += '(' + str(players) + ' / ' + str(max_players) + ')'
            if in_game:
                l+= ' -- CLOSED'
            else:
                l+= ' -- OPEN'
            self.game_list_list[l] = game

        self.view_game_page(self.game_list_page)

    def remote_sendLobbyUsersList(self, users):
        self.server_lobby_users.entries = users
        self.server_lobby_users.build_entries()

    #end game lobby view


    #main update loop
    def update(self):
        self.event_handler.update()
        if self.event_handler.quit:
            pygame.quit()
            self.disconnect()
            self.close()
            return None

        self.screen.fill((0,0,0))
        if self.playing:
            #handle game play events/rendering
            pass
        self.event_handler.gui.render()
        pygame.display.flip()

def main():
    g = Engine()

main()
