<script>
	import { StartCardState } from '$lib/components';
	import StartCard from './StartCard.svelte';
</script>

<StartCard
	title="Create Local"
	description="Create an archive from scratch to save channels/playlists"
	href="/create"
	ballKind={0}
	state={StartCardState.Enabled}
/>
