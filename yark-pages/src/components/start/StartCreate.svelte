<script>
	import StartCard from './StartCard.svelte';
</script>

<StartCard
	title="Create Local"
	description="Create an archive from scratch to save your channels + playlists"
	href="/create/local"
	ballKind={0}
	half
>
	<p class="update">Stay tuned for more..</p>
</StartCard>

<style lang="scss">
	.update {
		color: gray;
		font-size: small;
		bottom: 0;
	}
</style>
