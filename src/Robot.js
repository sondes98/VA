import React from 'react';
import "./Robot.css";

function Robot() {
  return (
    <div className="container">
    <div className="robot-design">
      <div className="robot-head">
        <div className="robot-head_antenna" />
        <div className="robot-head_antenna-dot" />
        <div className="robot-head_face">
          <div className="robot-head_eye left" />
          <div className="robot-head_eye right" />
          <div className="robot-head_mouth" />
        </div>
      </div>
      <div className="robot-body">
        <div className="robot-body_arm left" />
        <div className="robot-body_arm right" />
        <div className="robot-body_chest">
          <div className="heart">
            <div className="robot-body_chest-heart" />
          </div>
        </div>
        <div className="robot-body_boosts">
          <div className="robot-body_boosts-line" />
          <div className="robot-body_boosts-line" />
          <div className="robot-body_boosts-line" />
        </div>
      </div>
    </div>
  </div>
  
  );
}

export default Robot;
