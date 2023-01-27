<script lang="ts">
	import LoadList from '../../../components/start/LoadList.svelte';
	import StartCard from '../../../components/start/StartCard.svelte';
</script>

<div class="container">
	<StartCard
		title="Load Existing"
		description="Manage/view an existing archive that you've already created"
		ballKind={1}
		width={`${18 * 2 + 6 + 0.1}rem`}
	>
		<LoadList count={10} />
	</StartCard>
</div>

<style lang="scss">
	.container {
		display: flex;
		justify-content: center;
	}
</style>
