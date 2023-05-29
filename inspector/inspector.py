# Copyright: (c) 2019 Hikaru Y. <hkrysg@gmail.com>
# Copyright: (c) 2023 mizmu addons https://github.com/hafatsat-anki

from inspect import stack
from typing import Any

import aqt
from PyQt6 import QtWidgets, QtCore
from anki.hooks import addHook
from aqt import mw
from aqt.qt import *
from aqt.utils import tooltip, tr, saveGeom, maybeHideClose, restoreGeom
from aqt.webview import AnkiWebView

ADDON = 'AnkiWebView Inspector'
CONTEXT_MENU_ITEM_NAME = 'Inspect'
FONT_SIZE = 12
QDOCKWIDGET_STYLE = '''
    QDockWidget::title {
        padding-top: 0;
        padding-bottom: 0;
    }
'''


class Inspector(QDockWidget):
    """
    Dockable panel with Qt WebEngine Developer Tools
    """

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setObjectName(ADDON)
        self.setAllowedAreas(
            Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea|Qt.BottomDockWidgetArea)
        self.toggleViewAction().setText('Toggle Inspector')
        # make the title bar thinner
        self.setStyleSheet(QDOCKWIDGET_STYLE)
        self.web = None
        self.setup_hooks()

    def setup_hooks(self):
        # メインウィンドウ起動時にはパネルを閉じておく
        addHook('profileLoaded', self.hide)
        # プロファイル切り替え時にwebをdelete
        addHook('unloadProfile', self.delete_web)
        addHook('AnkiWebView.contextMenuEvent', self.on_context_menu_event)
        addHook('EditorWebView.contextMenuEvent', self.on_context_menu_event)
        addHook('beforeStateChange', self.on_anki_state_change)

    def on_context_menu_event(self, web, menu):
        # a = QAction(CONTEXT_MENU_ITEM_NAME)
        # a.triggered.connect(lambda: self.setup_web(web.page()))
        # a.setShortcut("ctrl+shift+x")
        # menu.addAction(a)
        menu.addAction(CONTEXT_MENU_ITEM_NAME, lambda: self.setup_web(web.page()))

    def setup_web(self, page):
        if self.web:
            self.web.deleteLater()
        self.web = QWebEngineView(mw)
        self.web.setMinimumWidth(240)

        # font size
        ws = self.web.settings()
        ws.setFontSize(QWebEngineSettings.MinimumFontSize, FONT_SIZE)
        ws.setFontSize(QWebEngineSettings.MinimumLogicalFontSize, FONT_SIZE)
        ws.setFontSize(QWebEngineSettings.DefaultFontSize, FONT_SIZE)

        # "Uncaught ReferenceError: qt is not defined"を防ぐために
        # AnkiWebViewと同じwebChannelを使う
        channel = mw.web._page.webChannel()
        self.web.page().setWebChannel(channel)

        self.web.page().setInspectedPage(page)
        self.setWidget(self.web)
        # make sure the panel is docked to main window when displaying
        self.setFloating(False)
        self.show()

    def on_anki_state_change(self, *_):
        """
        パネルを閉じた状態でAnkiのstateが変わったらwebをdelete
        """
        if self.isHidden():
            self.delete_web()
    
    def delete_web(self):
        if self.web:
            self.web.deleteLater()
            self.web = None


def check_qt_version():
    """
    setInspectedPage, setDevToolsPageはQt5.11以降対応なのでチェックする
    """
    qt_ver = QT_VERSION_STR.split('.')
    if int(qt_ver[1]) < 11:
        return False
    else:
        return True


def main():
    # if not check_qt_version():
    #     return
    inspector = Inspector('', mw)
    mw.addDockWidget(Qt.RightDockWidgetArea, inspector)


main()

# (❁´◡`❁) inspector in new window (●'◡'●)

class inspector(object):
    def setupUi(self, Dialog, page):
        self.centralwidget = QWidget(Dialog)
        Dialog.setWindowTitle("inspect")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setMaximumHeight(16)
        self.verticalLayout.addWidget(self.label)
        self.web = QWebEngineView(parent=Dialog)
        channel = mw.web._page.webChannel()
        self.web.page().setWebChannel(channel)
        self.web.page().setInspectedPage(page)
        self.verticalLayout.addWidget(self.web)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.label.setTextFormat(Qt.TextFormat.RichText)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.label.setOpenExternalLinks(True)
        self.label.setText("<html><head/><body><p align=\"center\"><a href=\"https://ankiweb.net/shared/byauthor/760817185\"><span style=\" text-decoration: underline; color:#00aaff;\">&lt;mizmu_addons&gt;</span>    </a><a href=\"https://github.com/hafatsat-anki\"><span style=\" text-decoration: underline; color:#000000;\">&lt;github&gt;</span>    </a><a href=\"https://www.patreon.com/mizmuaddons\"><span style=\" text-decoration: underline; color:#ff0000;\">&lt;patreon&gt;</span>    </a><a href=\"https://www.buymeacoffee.com/jhhomshl\"><span style=\" text-decoration: underline; color:#bfbf00;\">&lt;buymeacoffee&gt;</span></a></p></body></html>")

        Dialog.setCentralWidget(self.centralwidget)


class Newinspector(QMainWindow):
    def __init__(self, page=None) -> None:
        super().__init__(None, Qt.WindowType.Window)

        self.name = "inspector"
        self.form = inspector()
        # self.setMinimumWidth(700)
        # self.setMinimumHeight(800)
        f = self.form
        f.setupUi(self, page)
        self.show()
        restoreGeom(self, "inspector")
        self.activateWindow()

    def closeWithCallback(self, onsuccess: Callable) -> None:
        saveGeom(self, "inspector")
        aqt.dialogs.markClosed("inspector")
        self.close()
        onsuccess()


def on_context_menu_event(web, menu):
    menu.addAction("inspector in new window", lambda: aqt.dialogs.open("inspector", page=web.page()))

aqt.DialogManager._dialogs["inspector"] = [Newinspector, None]
addHook('AnkiWebView.contextMenuEvent', on_context_menu_event)
addHook('EditorWebView.contextMenuEvent', on_context_menu_event)


# next code from Add-on number 354407385 https://ankiweb.net/shared/info/354407385 to open multiple inspectors

aqt.DialogManager._openDialogs = list()

# init
old_init = aqt.DialogManager.__init__

def __init__(self, oldDialog=None):
    if oldDialog is not None:
        aqt.DialogManagerMultiple._dialogs = oldDialog._dialogs
    old_init(self)
aqt.DialogManager.__init__ = __init__

# open
aqt.DialogManager.old_open = aqt.DialogManager.open
def open(self, name, *args, **kwargs):
    """Open a new window, with name and args.

    Or reopen the window name, if it should be single in the
    config, and is already opened.
    """
    function = self.openMany if  name == "inspector" else self.old_open
    return function(name, *args, **kwargs)
aqt.DialogManager.open = open

# openMany
def openMany(self, name, *args, **kwargs):
    """Open a new window whose kind is name.

    keyword arguments:
    args -- values passed to the opener.
    name -- the name of the window to open
    """
    (creator, _) = self._dialogs[name]
    instance = creator(*args, **kwargs)
    self._openDialogs.append(instance)
    return instance
aqt.DialogManager.openMany = openMany

# markClosedMultiple
def markClosedMultiple(self):
    caller = stack()[2].frame.f_locals['self']
    if caller in self._openDialogs:
        self._openDialogs.remove(caller)
aqt.DialogManager.markClosedMultiple = markClosedMultiple

# markClosed
old_markClosed = aqt.DialogManager.markClosed
def markClosed(self, name):
    """Remove the window of windowName from the set of windows. """
    # If it is a window of kind single, then call super
    # Otherwise, use inspect to figure out which is the caller
    if name == "inspector":
        self.markClosedMultiple()
    else:
        old_markClosed(self, name)
aqt.DialogManager.markClosed = markClosed

# allClosed
old_allClosed = aqt.DialogManager.allClosed
def allClosed(self):
    """
    Whether all windows (except the main window) are marked as
    closed.
    """
    return self._openDialogs == [] and old_allClosed(self)
aqt.DialogManager.allClosed = allClosed

# closeAll
old_closeAll = aqt.DialogManager.closeAll
def closeAll(self, onsuccess):
    """Close all windows (except the main one). Call onsuccess when it's done.

    Return True if some window needed closing.
    None otherwise

    Keyword arguments:
    onsuccess -- the function to call when the last window is closed.
    """
    def callback():
        """Call onsuccess if all window (except main) are closed."""
        if self.allClosed():
            onsuccess()
        else:
            # still waiting for others to close
            pass
    if self.allClosed():
        onsuccess()
        return

    for instance in self._openDialogs:
        # It should be useless. I prefer to keep it to avoid erros
        if not sip.isdeleted(instance):
            if getattr(instance, "silentlyClose", False):
                instance.close()
                callback()
            else:
                instance.closeWithCallback(callback)

    return old_closeAll(self, onsuccess)
aqt.DialogManager.closeAll = closeAll
