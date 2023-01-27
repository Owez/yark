<script lang="ts">
	export let width: string = '10rem';
	export let height: string = '10rem';

	let style = `width: ${width};height: ${height};`;
</script>

<div class="card" {style}>
	<slot />
</div>

<style lang="scss">
	.card {
		margin: 1.5rem;
		border: 1px solid rgba($color: #000000, $alpha: 0.12);
		border-radius: 15px;
		padding: 1.5rem;
	}
</style>
