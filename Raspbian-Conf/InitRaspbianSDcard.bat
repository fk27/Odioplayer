@ECHO OFF
CLS
ECHO *************************************
ECHO * OdioPlayer copy files to raspbian *
ECHO *************************************

SETLOCAL

wmic logicaldisk get drivetype, deviceid, volumename, description

ECHO Enter Raspbian boot drive (only the letter)
SET /p bootDrive=

ECHO:
ECHO Enter Raspbian rootfs drive (only the letter)
SET /p rootfsDrive=

ECHO:
ECHO Confirm %bootDrive%: as the raspbian boot drive? [y,n]
SET /p bootConfirm=

ECHO:
ECHO Confirm %rootfsDrive%: as the raspbian rootfs drive? [y,n]
SET /p rootfsConfirm=

ECHO:
IF EXIST %bootDrive%:\ (
	ECHO %bootDrive%: drive found
	IF %bootConfirm% == y (
		ECHO Raspbian Initial boot copy: Started
		xcopy /s /y /q ".\boot" %bootDrive%:
	) ELSE (
		ECHO Raspbian Initial boot copy: Canceled
	)
) ELSE (
	ECHO Raspbian Initial boot copy: Drive not found
)

ECHO:
IF EXIST %rootfsDrive%:\ (
	ECHO %rootfsDrive%: drive found
	IF %rootfsConfirm% == y (
		ECHO Raspbian Initial rootfs copy: Started
		xcopy /s /y /q ".\rootfs" %rootfsDrive%:
	) ELSE (
		ECHO Raspbian Initial rootfs copy: Canceled
	)
) ELSE (
	ECHO Raspbian Initial rootfs copy: Drive not found
)


ECHO: 
ECHO Press enter to exit
SET /p input=

ENDLOCAL