<script lang="ts">
    import type { LayoutServerData } from "./$types";

    export let data: LayoutServerData;
</script>

<h1 class="dash-title">{data.archiveState.name}'s {data.archiveKind}</h1>
<slot />
