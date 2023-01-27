<script>
	import StartCard from './StartCard.svelte';
</script>

<a href="/create/local" class="invis">
	<StartCard
		title="Create Local"
		description="Create an archive from scratch to save your channels + playlists"
		ballKind={0}
	>
		<p class="update">Stay tuned for more..</p>
	</StartCard>
</a>

<style lang="scss">
	.update {
		color: gray;
		font-size: small;
		bottom: 0;
	}
</style>
