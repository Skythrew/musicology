APP_ID='io.github.skythrew.musicology'

DISCORD_RPC_ID='1387060938250653799'

WEBVIEW_HTML="""
<!DOCTYPE html>
<html>
  <body>
    <div id="player"></div>

    <script>
      var tag = document.createElement('script');

      tag.src = "https://www.youtube.com/iframe_api";
      var firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

      var player;
      function onYouTubeIframeAPIReady() {
        player = new YT.Player('player', {
          height: '390',
          width: '640',
          playerVars: {
            'playsinline': 1
          },
          events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
          }
        });
      }

      function loadSingleSong(id) {
        player.loadVideoById(id);
        player.playVideo();
      }

      function getPlayerInfos() {
        return [player.getCurrentTime(), player.getDuration(), player.getPlayerState()];
      }

      function onPlayerReady(event) {

      }

      function onPlayerStateChange(event) {

      }
    </script>
  </body>
</html>
"""
