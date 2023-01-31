<script lang="ts">
	import { StartCardState } from '$lib/components';
	import StartCard from './StartCard.svelte';
</script>

<StartCard
	title="Connect"
	description="View someone else's federated archive server"
	href="/load/federated"
	ballKind={2}
	state={StartCardState.Enabled}
	margin="1.5rem 0 0 0"
/>
