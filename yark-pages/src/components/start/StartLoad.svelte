<script lang="ts">
	import LoadList from './LoadList.svelte';
	import StartCard from './StartCard.svelte';
</script>

<a href="/load" class="invis">
	<StartCard
		title="Load Existing"
		description="Manage/view an existing archive that you’ve already created"
		ballKind={1}
	>
		<LoadList />
	</StartCard>
</a>
