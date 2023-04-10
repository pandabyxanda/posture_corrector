import json
import os
import sys

import wx
import wx.adv

from src.opencv_detector import Detector


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


TRAY_ICON = resource_path("..\\res\\tray_image.png")


class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        frame.task_bar_icon = self
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.frame.task_bar_icon = self
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    @staticmethod
    def create_menu_item(menu, label, func, enabled=True):
        item = wx.MenuItem(menu, -1, label)
        item.Enable(enabled)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.Append(item)
        return item

    def CreatePopupMenu(self):
        menu = wx.Menu()

        self.create_menu_item(menu, 'Empty...', lambda event: None, enabled=False)

        menu.AppendSeparator()
        self.create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path, text=""):
        icon = wx.Icon(path)
        self.SetIcon(icon, text)

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.frame.Destroy()

    def on_left_down(self, event):
        print('Tray icon was left-clicked.')
        print(f"{self.frame.IsIconized() = }")

        if self.frame.IsIconized():
            self.frame.Show()
            self.frame.Iconize(iconize=False)

        else:
            self.frame.Hide()
            self.frame.Iconize(iconize=True)


class PopupWindow(wx.Frame):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance:
            cls.__instance.Close()
        cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, parent, pos=(0, 0), message=''):
        self.parent = parent
        size = (300, 50)
        # pos = (mouse_pos[0], mouse_pos[1] - size[1] - 20)
        wx.Frame.__init__(self, parent, title="title1", size=size,
                          pos=pos,
                          style=wx.STAY_ON_TOP | wx.FRAME_NO_TASKBAR)
        self.SetBackgroundColour("#f9f7e9")
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(12)

        # message_list = message.split("\r\n")
        # if len(message_list) == 1 and len(message_list[0]) > 100:
        #     message = message_list[0]
        #     n = 100
        #     message_list = [message[i:i + n] for i in range(0, len(message), n)]
        #
        # if len(message_list) == 1:
        #     message_list = [message_list[0].strip()]
        #
        # self.st = []
        # text_width, text_height = 0, 0
        # for i in range(0, len(message_list)):
        #     st_t = wx.StaticText(self, label=message_list[i], pos=(0, 0))
        #     st_t.SetFont(font)
        #     self.st.append(st_t)
        #     dc = wx.ClientDC(self.st[i])
        #     text_dimensions = dc.GetTextExtent(self.st[i].GetLabel())
        #     if text_dimensions[0] > text_width:
        #         text_width = text_dimensions[0]
        #     if text_dimensions[1] > text_height:
        #         text_height = text_dimensions[1]
        #
        displays = [wx.Display(i) for i in range(wx.Display.GetCount())]
        active_display = wx.Display.GetFromPoint(wx.GetMousePosition())
        display_rect = displays[active_display].GetGeometry()
        width, height = display_rect.GetSize()
        # x, y = mouse_pos[0] - display_rect.x, mouse_pos[0] - display_rect.y
        pos = (width // 2, height // 2)
        size = (400, 50)
        # if mouse_pos[0] - display_rect.x - size[0] < 20:
        #     pos = (display_rect.x + 20, mouse_pos[1] - size[1] - 20)
        # else:
        #     pos = (mouse_pos[0] - size[0], mouse_pos[1] - size[1] - 20)
        #
        st_1 = wx.StaticText(self, label=f"{message}", pos=(0, 0))
        st_1.SetFont(font)
        st_2 = wx.StaticText(self, label=f"Sit in the correct posture", pos=(0, 20))
        st_2.SetFont(font)
        # self.st.append(st_t)
        # dc = wx.ClientDC(self.st[i])

        self.SetPosition(pos)
        self.SetSize(size)
        #
        # for i in range(0, len(self.st)):
        #     self.st[i].SetPosition((10, i * text_height + 10 - 2))
        self.Bind(wx.EVT_LEFT_DOWN, self.on_key_pressed, id=wx.ID_ANY)
        self.Bind(wx.EVT_MOTION, self.on_mouse_moved, id=wx.ID_ANY)

        self.timer1 = wx.Timer(self)
        self.timer1.Start(1000)
        self.Bind(wx.EVT_TIMER, self.on_timer1, self.timer1)
        self.Show()

    def on_mouse_moved(self, event):
        self.parent.wnd = None
        # print("mouse moved")
        self.Close()

    def on_key_pressed(self, event):
        # print("Key pressed")
        self.Close()

    def on_timer1(self, event):
        self.timer1.Stop()
        self.parent.wnd = None
        self.Close()
        # self.Destroy()



class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(500, 400),
                          style=wx.RESIZE_BORDER | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)


        try:
            with open('parametrs.json', 'r') as outfile:
                params = json.load(outfile)
            if len(params) != 1:
                raise IOError('Invalid parameters')
        except IOError:
            params = {
                "angle": 10,
            }

        self.wnd = None

        self.timer = wx.Timer(self)
        self.timer.Start(1000)

        self.detector = Detector(0)

        self.angle = params["angle"]

        self.panel = wx.Panel(self)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)

        self.spin_ctrl1 = wx.SpinCtrl(
            self.panel, id=wx.ID_ANY, pos=(200, 0),
            size=wx.DefaultSize, style=wx.SP_ARROW_KEYS, min=1, max=1000, initial=self.angle,
            name="wxSpinCtrl"
        )
        self.text = wx.StaticText(self.panel, label="Angle:")
        self.text_current = wx.StaticText(self.panel, label="Current angle = None")
        # tc = wx.TextCtrl(self.panel)
        self.hbox1.Add(self.text, flag=wx.RIGHT, border=8)
        self.hbox1.Add(self.spin_ctrl1, flag=wx.RIGHT, border=8)
        self.hbox1.Add(self.text_current, flag=wx.RIGHT, border=8)

        self.vbox.Add(self.hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        self.panel.SetSizer(self.vbox)
        self.Iconize()
        # self.Show()



        self.Bind(wx.EVT_CLOSE, self.on_minimize)
        self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.Bind(wx.EVT_SPINCTRL, self.on_spin_ctrl1, id=self.spin_ctrl1.GetId())
        self.counter = 1

    def on_minimize(self, event):
        print("minimizing window")
        self.Iconize()
        self.Hide()
        # self.task_bar_icon.set_icon(TRAY_ICON2)
        # wx.CallAfter(self.Destroy)
        # self.Close()
    def on_spin_ctrl1(self, event):
        # self.time_before_break = self.spin_ctrl_work_time.GetValue() * 60
        # t = time.strftime('%M:%S', time.gmtime(self.time_before_break))
        # self.st4.Label = str(t)
        self.save_params_to_json()
        print(f"spin changed to {self.spin_ctrl1.GetValue()}")
        self.angle = self.spin_ctrl1.GetValue()

    def on_timer(self, event):
        # print(f"timer")
        angle = self.detector.check_posture(self.angle)
        if angle:
            self.text_current.SetLabel(f"Current angle = {angle}")
            if angle > self.angle:
                print(f"{self.counter = }")
                self.counter += 1
            else:
                self.counter = 1
            if self.counter % 5 == 0:
                self.counter = 1
                self.create_alert_window(event, angle=angle)

    # def close_window(self):
    #     if self.wnd:
    #         self.wnd.Close()

    def create_alert_window(self, event, angle='<empty>'):
        if not self.wnd:
            self.wnd = PopupWindow(self, (300, 200), message=f"Max angle = {self.angle}, current angle = {angle}")

    def save_params_to_json(self):
        x = {
            "angle": self.spin_ctrl1.GetValue(),
        }

        with open('parametrs.json', 'w') as outfile:
            json.dump(x, outfile, indent=4)


class App(wx.App):
    def __init__(self, redirect):
        super().__init__(redirect=redirect)
        self.frame = None

    def OnInit(self):
        self.frame = MainWindow(None, "Posture corrector")
        # wx.lib.inspection.InspectionTool().Show()  # to inspect all parameters of windows\panels\widgets
        TaskBarIcon(self.frame)
        return True


if __name__ == "__main__":
    app = App(redirect=False)
    app.MainLoop()
    print("Exiting app correctly...")
