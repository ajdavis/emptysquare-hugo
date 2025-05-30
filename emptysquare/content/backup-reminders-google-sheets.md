+++
type = "post"
title = "Reminding Myself to Back Up My Drives, With Google Sheets"
date = "2016-05-09T08:33:19"
description = "I maintain my photo archive's offsite backup with a little Javascript and a tiny Pelican case."
category = ["Programming"]
tag = []
enable_lightbox = false
thumbnail = "pelican.jpg"
draft = false
+++

<p>My photo archive is the only data I have that's precious enough to back up, and too big to back up in the cloud. Nevertherless, I procrastinate about making backups. I especially procrastinate about swapping my home backups with the offsite ones at my office. Until now.</p>
<h1 id="my-rig">My Rig</h1>
<p>The photo archive lives on a Seagate 4 TB hard drive, and I back it up to two other 4 TB drives. Yet two more 4 TB drives are Time Machine backups for the system drive on my laptop. I swap these drives in and out of a Mediasonic HF2-SU3S2 enclosure with 4 bays. It's cheap, remarkably small, and does the job.</p>
<p><img alt="Description: a Mediasonic ProBox HF2-SU3S2, a black plastic hard drive enclosure." src="mediasonic.jpg"/></p>
<p>In theory, I frequently back up my photos and my system hard drive to the external drives, and occasionally swap these drives with backups I keep at the office in case of a catastrophe at my apartment. In practice, I don't.</p>
<h1 id="calculate-age-of-backups">Calculate Age of Backups</h1>
<p>This weekend I decided to get my act together. The first thing was to design a spreadsheet to track the age of my home and offsite backups for my photos and my system drive.</p>
<table cellpadding="0" cellspacing="0" width="100%">
<tr style="height:16px; font-weight: bold">
<td dir="ltr">drive</td>
<td dir="ltr">data</td>
<td dir="ltr">location</td>
<td dir="rtl">backed up</td>
</tr>
<tr style="height:16px;">
<td dir="ltr">Photos 4TB backup 1</td>
<td dir="ltr">photos</td>
<td dir="ltr">home</td>
<td dir="rtl">3/28/2016</td>
</tr>
<tr style="height:16px;">
<td dir="ltr">Photos 4TB backup 2</td>
<td dir="ltr">photos</td>
<td dir="ltr">home</td>
<td dir="rtl">5/8/2016</td>
</tr>
<tr style="height:16px;">
<td dir="ltr">TimeMachine 4TB 1</td>
<td dir="ltr">system</td>
<td dir="ltr">home</td>
<td dir="rtl">5/5/2016</td>
</tr>
<tr style="height:16px;">
<td dir="ltr">TimeMachine 4TB 2</td>
<td dir="ltr">system</td>
<td dir="ltr">office</td>
<td dir="rtl">4/3/2016</td>
</tr>
</table>
<p>I put that in Google Sheets. Whenever I take a backup or schlep a drive between my home and office, I manually update the spreadsheet.</p>
<p>How do I calculate the age of the newest backup for "photos"? It's today's date, minus the maximum "backed up" entry where "data" equals "photos". After some futzing with Google Sheets syntax, I came up with:</p>

{{<highlight plain>}}
=ROUND(NOW()-MAX(FILTER(D2:D5, B2:B5 = "photos")))
{{< / highlight >}}

<p>That's the newest photos backup anywhere. I also want to calculate the newest photos backup at the office specifically, so I make a second formula that requires the "location" column to be "office":</p>

{{<highlight plain>}}
=ROUND(NOW()-MAX(FILTER(D2:D5, B2:B5 = "photos", C2:C5 = "office")))
{{< / highlight >}}

<p>I do the same for my "system" data set. Now I know the age of my backups:</p>
<table class="table table-striped">
<tr style="height:16px; font-weight: bold">
<td dir="ltr">data</td>
<td dir="ltr">Last backup (days)</td>
<td dir="ltr">Last offsite backup</td>
</tr>
<tr>
<td>photos</td>
<td>0</td>
<td>#N/A</td>
</tr>
<tr>
<td>system</td>
<td>3</td>
<td>35</td>
</tr>
</table>
<p>You can see how I've procrastinated. I haven't lugged a copy of my system backup to the office in a month, and I don't have <em>any</em> offsite backup of my photo archive now. Someone should nag me!</p>
<h1 id="nag-me">Nag Me</h1>
<p>I've decided it's worth the trouble to take backups at least every 4 days, and keep offsite backups fresher than 14 days old. Following <a href="https://www.withoutthesarcasm.com/automating-google-spreadsheets-email-reminders/">this excellent guide to Google Sheets automation</a>, I wrote <a href="https://gist.github.com/ajdavis/458442bc63b757f13cd0c1cbd689198f">some Javascript to check once a day whether my backups are fresh</a>. The nut is this:</p>

{{<highlight javascript>}}
var warnings = [];
// Set datum to "photos" or "system".
var datum = ...; 
// Get the row with the age-of-backups calculation.
var backupsRow = ...;
var lastBackup = sheet.getSheetValues(backupsRow, 2, 1, 1)[0][0];
var lastOffsite = sheet.getSheetValues(backupsRow, 3, 1, 1)[0][0];

if (lastBackup === "#N/A") {
  warnings.push("No " + datum + " backups.");
} else if (lastBackup > backupFreq) {
  warnings.push("No " + datum + " backups in " 
    + lastBackup + " days.");
}

if (lastOffsite === "#N/A") {
  warnings.push("No " + datum + " offsite backups.");
} else if (lastOffsite > offsiteFreq) {
  warnings.push("No " + datum + " offsite backups in " 
    + lastOffsite + " days.");
}
{{< / highlight >}}

<p>The script checks that each data set's newest backup is at most <code>backupFreq</code> old, which is 4 days. Then it does the same for the offsite backups, checking they're at most 14 days old.</p>
<p>If there are any warnings it emails me:</p>

{{<highlight javascript>}}
if (warnings.length) {
  var msg = warnings.join("\n\n") + 
    "\n\n(Intend backups every " + backupFreq + " days, " +
    "offsite backups every " + offsiteFreq + " days.)";

  MailApp.sendEmail("jesse@emptysquare.net", "Backup reminders", msg);
}
{{< / highlight >}}

<p>This morning it emailed me:</p>

{{<highlight plain>}}
Subject: Backup reminders

No photos offsite backups.

No system offsite backups in 36 days.

(Intend backups every 4 days, offsite backups every 14 days.)
{{< / highlight >}}

<p>I added logic to only email me weekday mornings, since that's when I can swap the drives I keep at home and the office. I bike to work up First Avenue and across Times Square through rush hour's barbarian traffic, so I need to encase the drive in something crash-proof. The Pelican 1060 seems doughty enough:</p>
<p><img alt="" src="pelican.jpg"/></p>
<p>It's 60 degrees and clear this morning so I'm going to put my photo archive in this thing, throw it in my bag and bike to work. One more swap after this one and I'll satisfy my nagging script. My backups will finally be in order. What a relief!</p>
