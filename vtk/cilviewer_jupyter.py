from trame.app import get_server
from trame.decorators import TrameApp, change
from trame.widgets import vuetify3 as v3, vtk as vtk_widgets
from trame.ui.vuetify3 import SinglePageLayout
import vtk




from ccpi.viewer import CILViewer2D
@TrameApp()
class iviewer:
    
    def __init__(self, server=None):
        self.server = get_server(server)
        self._init_vtk()
        
    @property
    def state(self):
        return self.server.state

    @property
    def ctrl(self):
        return self.server.controller
    
    def _init_vtk(self):
        self.cil_viewer = CILViewer2D.CILViewer2D(enableSliderWidget=False)
        self.cil_viewer.renWin.SetOffScreenRendering(1)
        self._add_observers()

    def _add_observers(self):
        """Add observer to sync the view slice with the mouse wheel event"""
        style = self.cil_viewer.style
        priority = 1 - 0.1
        style.AddObserver("MouseWheelForwardEvent", self._handle_mouse_wheel, priority)
        style.AddObserver("MouseWheelBackwardEvent", self._handle_mouse_wheel, priority)
    
    def _handle_mouse_wheel(self, obj, event):
        """Update the view slice when the mouse wheel is used"""
        self.view_slice = self.cil_viewer.getActiveSlice()
        
    def setInput(self, image):
        self.cil_viewer.setInputData(image)
        # TODO find a way to set the slider limits after the ui has been built
        self._build_ui()

    def _build_ui(self):
        with SinglePageLayout(self.server, full_height=True) as layout:
            self.ui = layout

            layout.icon.click = self.ctrl.view_reset_camera
            layout.title.set_text("CILViewer in jupyter lab!")

            with layout.toolbar:
                v3.VSpacer()
                self.extent = self.cil_viewer.img3D.GetExtent()
                default_slice = (self.extent[self.cil_viewer.sliceOrientation * 2] + \
                                 self.extent[self.cil_viewer.sliceOrientation * 2 +1]) // 2
                v3.VSlider(
                    v_model=("view_slice", default_slice),
                    min=self.extent[self.cil_viewer.sliceOrientation * 2],
                    max=self.extent[self.cil_viewer.sliceOrientation * 2 + 1], 
                    step=1,
                    hide_details=True, style="max-width: 300px",
                )
                v3.VLabel("Current slice {{ view_slice }} ")
                v3.VDivider(vertical=True, classes="mx-2")
                v3.VBtn(icon="mdi-undo-variant", click=self.reset_resolution)

            with layout.content:
                with v3.VContainer(fluid=True, classes="pa-0 fill-height"):
                    self.html_view = vtk_widgets.VtkRemoteView(self.cil_viewer.renWin, trame_server=self.server, ref="view")
                    self.ctrl.view_update = self.html_view.update
                    self.ctrl.view_reset_camera = self.html_view.reset_camera
                    self.ctrl.on_server_ready.add(self.html_view.update)
                    # self.ctrl.view_update = view.update
                    # self.ctrl.view_reset_camera = view.reset_camera
    
    def reset_resolution(self):
        self.resolution = 6

    @property
    def view_slice(self):
        return self.state.view_slice

    @view_slice.setter
    def view_slice(self, v):
        with self.state:
            self.state.view_slice = v

    @change("view_slice")
    def _on_view_slice_change(self, view_slice, **kwargs):
        self.cil_viewer.setActiveSlice(view_slice)
        self.cil_viewer.updatePipeline(resetcamera=False)
        self.ctrl.view_update()

def main():
    cone_app = iviewer()
    cone_app.server.start()


if __name__ == "__main__":
    main()
