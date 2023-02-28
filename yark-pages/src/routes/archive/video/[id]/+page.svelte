<script lang="ts">
	import { getCurrentElement } from '$lib/element';
	import BackButton from '../../../../components/video/BackButton.svelte';
	import Description from '../../../../components/video/Description.svelte';
	import History from '../../../../components/video/History.svelte';
	import Player from '../../../../components/video/Player.svelte';
	import TopInfo from '../../../../components/video/TopInfo.svelte';
	import type { PageData } from './$types';

	export let data: PageData;
</script>

<!-- Core content -->
<BackButton />
<Player video_id={data.video_id} />
<h1 class="video">{getCurrentElement(data.video.title)}</h1>
<TopInfo video_id={data.video_id} video={data.video} />
<Description video={data.video} />
<!-- ~Below page fold -->
<History video={data.video} />
