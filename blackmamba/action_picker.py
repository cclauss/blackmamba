#!python3

from objc_util import on_main_thread, ObjCClass
from ui import TableViewCell, Image
import ui
from blackmamba.picker import load_picker_view, PickerItem, PickerDataSource
from blackmamba.uikit import UITableViewCellStyleSubtitle
import blackmamba.ide
import os
        
        
class ActionInfo(object):
    def __init__(self, action_info):
        self.script_name = str(action_info['scriptName'])
        self.icon_name = str(action_info['iconName'])
        
        if action_info['title']:
            self.title = str(action_info['title'])
        else:
            self.title = None
            
        if action_info['iconColor']:
            self.icon_color = '#{}'.format(action_info['iconColor'])
        else:
            self.icon_color = '#FFFFFF'
                
                
def load_editor_actions():
    NSUserDefaults = ObjCClass('NSUserDefaults')
    defaults = NSUserDefaults.standardUserDefaults()
    return [ActionInfo(a) for a in defaults.objectForKey_('EditorActionInfos')]

                
class ActionPickerItem(PickerItem):
    def __init__(self, action_info):
        if not isinstance(action_info, ActionInfo):
            action_info = ActionInfo(action_info)
        
        if action_info.title:
            title = action_info.title
        else:
            _, tail = os.path.split(action_info.script_name)
            title, _ = os.path.splitext(tail)
        
        subtitle = ' • '.join(action_info.script_name.split(os.sep))
                
        super().__init__(title, subtitle)

        self.action_info = action_info
        
    @property
    def image(self):
        # TODO - Find a way how get the right icon, because there's
        #        lot of prefixes like iob:, different sizes, ...
        image = Image.named('iob:play_32')
        return image


class ActionPickerDataSource(PickerDataSource):
    def __init__(self):
        super().__init__()
        self.items = [ActionPickerItem(ai) for ai in load_editor_actions()]
        
    def tableview_cell_for_row(self, tv, section, row):
        item = self.filtered_items[row]
        cell = TableViewCell(UITableViewCellStyleSubtitle)
        cell.text_label.number_of_lines = 1
        cell.text_label.text = item.title
        cell.detail_text_label.text = item.subtitle
        cell.detail_text_label.text_color = (0, 0, 0, 0.5)
        
#        cell.image_view.content_mode = ui.CONTENT_SCALE_ASPECT_FILL
#        cell.image_view.background_color = item.icon_color
#        cell.image_view.image = item.image
#        cell.image_view.alpha = 0.5
        
        return cell
                                                                                                    

@on_main_thread
def action_quickly():
    def run_wrench_item(item, shift_enter):
        blackmamba.ide.run_script(item.action_info.script_name)
                                                            
    v = load_picker_view()
    v.datasource = ActionPickerDataSource()
    v.shift_enter_enabled = False
    v.title_label.text = 'Action Quickly...'
    v.help_label.text = (
        '⇅ - select • Enter - run action item'
        '\n'
        'Esc - close • Ctrl [ - close with Apple smart keyboard'
    )
    v.textfield.placeholder = 'Start typing to filter wrench items...'
    v.did_select_item_action = run_wrench_item
    v.present('sheet', hide_title_bar=True)
    v.wait_modal()
    

if __name__ == '__main__':
    action_quickly()

