from trame.app import get_server
from trame.decorators import TrameApp, change
from trame.widgets import vuetify3 as v3, vtk as vtk_widgets
from trame.ui.vuetify3 import SinglePageLayout
import vtk


@TrameApp()
class Cone:
    def __init__(self, server=None):
        self.server = get_server(server)
        self._init_vtk()
        self._build_ui()

    @property
    def state(self):
        return self.server.state

    @property
    def ctrl(self):
        return self.server.controller

    def _init_vtk(self):
        renderer, render_window = vtk.vtkRenderer(), vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)

        render_window_interactor = vtk.vtkRenderWindowInteractor()
        render_window_interactor.SetRenderWindow(render_window)
        render_window_interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

        cone, mapper, actor = (
            vtk.vtkConeSource(),
            vtk.vtkPolyDataMapper(),
            vtk.vtkActor(),
        )

        mapper.SetInputConnection(cone.GetOutputPort())
        actor.SetMapper(mapper)
        renderer.AddActor(actor)
        renderer.ResetCamera()
        render_window.Render()

        self.render_window = render_window
        self.renderer = renderer
        self.actor = actor
        self.cone = cone

    @property
    def resolution(self):
        return self.state.resolution

    @resolution.setter
    def resolution(self, v):
        with self.state:
            self.state.resolution = v

    @change("resolution")
    def _on_resolution_change(self, resolution, **kwargs):
        self.cone.SetResolution(resolution)
        self.ctrl.view_update()

    def reset_resolution(self):
        self.resolution = 6

    def _build_ui(self):
        with SinglePageLayout(self.server, full_height=True) as layout:
            self.ui = layout

            layout.icon.click = self.ctrl.view_reset_camera
            layout.title.set_text("VTK Remote Rendering")

            with layout.toolbar:
                v3.VSpacer()
                v3.VSlider(
                    v_model=("resolution", 6),
                    min=3, max=60, step=1,
                    hide_details=True, style="max-width: 300px",
                )
                v3.VDivider(vertical=True, classes="mx-2")
                v3.VBtn(icon="mdi-undo-variant", click=self.reset_resolution)

            with layout.content:
                with v3.VContainer(fluid=True, classes="pa-0 fill-height"):
                    view = vtk_widgets.VtkRemoteView(
                        self.render_window, 
                        interactive_ratio=1,
                    )
                    self.ctrl.view_update = view.update
                    self.ctrl.view_reset_camera = view.reset_camera

from ccpi.viewer import CILViewer2D
from ccpi.viewer import viewer3D
@TrameApp()
class iviewer:
    
    def __init__(self, server=None):
        self.server = get_server(server)
        self._init_vtk()
        self._build_ui()

    @property
    def state(self):
        return self.server.state

    @property
    def ctrl(self):
        return self.server.controller
    def _init_vtk(self):
        # self.cil_viewer = 
        self.cil_viewer = viewer3D()
        self.cil_viewer.renWin.SetOffScreenRendering(1)

    def setInput(self, image):
        self.cil_viewer.setInputData(image)
        self.cil_viewer.style.ToggleVolumeVisibility()

    def _build_ui(self):
        with SinglePageLayout(self.server, full_height=True) as layout:
            self.ui = layout

            layout.icon.click = self.ctrl.view_reset_camera
            layout.title.set_text("CILViewer in jupyter lab!")

            with layout.toolbar:
                v3.VSpacer()
                v3.VSlider(
                    v_model=("resolution", 6),
                    min=3, max=60, step=1,
                    hide_details=True, style="max-width: 300px",
                )
                v3.VDivider(vertical=True, classes="mx-2")
                v3.VBtn(icon="mdi-undo-variant", click=self.reset_resolution)

            with layout.content:
                with v3.VContainer(fluid=True, classes="pa-0 fill-height"):
                    # view = vtk_widgets.VtkRemoteView(
                    #     self.render_window, 
                    #     interactive_ratio=1,
                    # )
                    self.html_view = vtk_widgets.VtkRemoteView(self.cil_viewer.renWin, trame_server=self.server, ref="view")
                    self.ctrl.view_update = self.html_view.update
                    self.ctrl.view_reset_camera = self.html_view.reset_camera
                    self.ctrl.on_server_ready.add(self.html_view.update)
                    # self.ctrl.view_update = view.update
                    # self.ctrl.view_reset_camera = view.reset_camera
    def reset_resolution(self):
        self.resolution = 6

def main():
    cone_app = Cone()
    cone_app.server.start()

def main_edo():
    cone_app = iviewer()
    import vtk
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName('head_uncompressed.mha')
    reader.Update()
    cone_app.setInput(reader.GetOutput())
    cone_app.server.start()

if __name__ == "__main__":
    main_edo()
