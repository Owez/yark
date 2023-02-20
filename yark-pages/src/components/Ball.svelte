<script lang="ts">
	export let kind = 0;

	$: src = `/img/ball${kind + 1}.png`;
</script>

<img {src} alt="Sphere Icon" />

<style lang="scss">
	img {
		$size: 45px;

		width: $size;
		height: $size;
	}
</style>
