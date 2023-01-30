<script>
	import { StartCardState } from '$lib/components';
	import StartCard from './StartCard.svelte';
</script>

<StartCard
	title="Create"
	description="Create an archive from scratch to save your channels + playlists"
	href="/create/local"
	ballKind={0}
	state={StartCardState.Half}
/>
