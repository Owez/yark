<script>
	import { StartCardState } from '$lib/components';
	import StartCard from '../../../../components/start/StartCard.svelte';
</script>

<div class="centre-h">
	<StartCard
		title="Connect"
		description="View someone else's federated archive server"
		ballKind={2}
		state={StartCardState.Max}
		margin="1.5rem 0 3rem 0"
	/>
</div>
