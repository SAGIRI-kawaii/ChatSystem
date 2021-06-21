<template>
	<view>
		<view>
			<view class="padding menu card-menu margin-top">
				<view class="cu-item">
					<view class="flex padding">
						<view class="cu-avatar xl round" style="background-image:url(https://ossweb-img.qq.com/images/lol/web201310/skin/big99008.jpg);"></view>
						<text class="padding margin-left text-xl">{{userdata.nickname}}</text>
					</view>
				</view>
			</view>
			
			<view class="cu-list menu card-menu">
				<view class="cu-item arrow">
					<button class="content flex" hover-class="none" @click="myfavorites" open-type="redirect">
						<text class="cuIcon-favorfill text-orange"></text>
						<text class="text-grey">个人信息修改</text>
					</button>
				</view>
				<view class="cu-item arrow">
					<button class="content flex" hover-class="none" @click="my_view_history" open-type="redirect">
						<text class="cuIcon-timefill text-orange"></text>
						<text class="text-grey">浏览记录</text>
					</button>
				</view>
				<view class="cu-item arrow">
					<button class="content flex" hover-class="none" @click="feedback" open-type="redirect">
						<text class="cuIcon-formfill text-orange"></text>
						<text class="text-grey">意见反馈</text>
					</button>
				</view>
				<view class="cu-item arrow">
					<button class="content flex" hover-class="none" @click="setting" open-type="redirect">
						<text class="cuIcon-settingsfill text-orange"></text>
						<text class="text-grey">设置</text>
					</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				title: 'Hello',
				PageCur: "my",
				userdata: {
					"nickname": "SAGIRI",
					"userId": 0,
					"name": "giao哥",
					"phone": 12345678901
				}
			}
		},
		onLoad() {
			// data init
		},
		methods: {
			my_address(){
				uni.navigateTo({
					url: "./my_address?userdata=" + encodeURIComponent(JSON.stringify(this.userdata))
				})
			},
			my_view_history(){
				uni.navigateTo({
					url: "./history_view?userdata=" + encodeURIComponent(JSON.stringify(this.userdata))
				})
			},
			service(){
				uni.navigateTo({
					url: "./service?userdata=" + encodeURIComponent(JSON.stringify(this.userdata))
				})
			},
			NavChange(e) {
				this.PageCur = e.currentTarget.dataset.cur
				uni.navigateTo({
					url: "../" + this.PageCur + "/index"
				})
			},
			master_app() {
				uni.showModal({
				    title: '我是师傅',
				    content: '确定前往急了吗——师傅端？',
				    success: function (res) {
				        if (res.confirm) {
				            console.log('用户点击确定');
				        } else if (res.cancel) {
				            console.log('用户点击取消');
				        }
				    }
				});
			}
		}
	}
</script>

<style>
	.bottom {
		padding-bottom: 0rpx;
		margin-bottom: 0rpx;
	}
	uni-page-head {
		display: none;
	}
	.order-button {
		font-size: 56rpx;
	}
</style>
