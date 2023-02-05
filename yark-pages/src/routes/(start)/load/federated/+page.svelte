<script lang="ts">
	import { StartCardState } from '$lib/components';
	import StartCard from '../../../../components/start/StartCard.svelte';
</script>

<div class="centre-h">
	<StartCard
		title="Connect"
		description="Connect to a remote federated archive server"
		ballKind={2}
		state={StartCardState.Max}
	>
		<!-- TODO -->
	</StartCard>
</div>
