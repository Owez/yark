<script lang="ts">
	import LoadList from './LoadList.svelte';
	import StartCard from './StartCard.svelte';
</script>

<StartCard
	title="Load Existing"
	description="Manage/view an existing archive that you've already created"
	link="/load"
	ballKind={1}
>
	<div class="list"><LoadList /></div>
</StartCard>

<style lang="scss">
	.list {
		margin-top: 1.25rem;
	}
</style>
