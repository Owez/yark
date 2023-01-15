"""Logging core for formatting output to users"""

class VideoLogger:
    @staticmethod
    def downloading(d):
        """Progress hook for video downloading"""
        # Get video's id
        id = d["info_dict"]["id"]

        # Downloading percent
        if d["status"] == "downloading":
            percent = d["_percent_str"].strip()
            print(
                Style.DIM + f"  • Downloading {id}, at {percent}.." + Style.NORMAL,
                end="\r",
            )

        # Finished a video's download
        elif d["status"] == "finished":
            print(
                Style.DIM
                + f"  • Downloaded {id}                               "
                + Style.NORMAL
            )

    def debug(self, msg):
        """Debug log messages, ignored"""
        pass

    def info(self, msg):
        """Info log messages ignored"""
        pass

    def warning(self, msg):
        """Warning log messages ignored"""
        pass

    def error(self, msg):
        """Error log messages"""
        pass
