<script>
    import HorizontalSelector from '../../../components/HorizontalSelector.svelte';
	import Separator from '../../../components/Separator.svelte';
	import Switch from '../../../components/Switch.svelte';
    import VerticalSelector from '../../../components/VerticalSelector.svelte';
    import { triggerEvent } from '../../../lib/events.ts';
</script>

<div class="flex flex-col w-104 m-6 ml-10 gap-8">
    <Separator orientation="horizontal" label="Units and Language" />
    <HorizontalSelector title="Display Units" 
                        description="The units ETS2LA will use when displaying information to a user. Scientific has only slight differences to metric."
                        options={["Metric", "Imperial", "Scientific"]}
                        onSelect={(index) => {
                            triggerEvent("settings:Update:StateSettings:DisplayUnits", index.toString());
                        }}
                        />
    <VerticalSelector title="Display Language" 
                      description="The language ETS2LA will use. Translations are provided by the community, we cannot guarantee their quality or accuracy."
                      options={["English", "Chinese (Simplified)", "Chinese (Traditional)", "French", "German", "Italian", "Japanese", "Korean", "Polish", "Portuguese (Brazilian)", "Russian", "Spanish"]}
                      onSelect={(index) => {
                          console.log("Selected index: ", index);
                      }}
                      />
    <Separator orientation="horizontal" label="Overlay" />
    <Switch title="Support Multiple Viewports"
            description="This allows ETS2LA to render multiple viewports, meaning you can move overlay windows to any monitor."
            />
    <Switch title="Limit Overlay Framerate"
            description="In most situations, over half of ETS2LA's CPU usage is spent for rendering the overlay. You can enable this to reduce CPU usage."
            />
    <Separator orientation="horizontal" label="3D Rendering" />
    <Switch title="Render AR Elements"
            description="We can render elements in the game world using our overlay. This will use additional CPU and GPU resource. It is recommended to keep this option enabled."
            />
    <Switch title="Simplified Graphics"
            description="Using simplified graphics can improve performance on lower-end hardware, or fix situations in which advanced features like shaders are not supported."
            />
</div>