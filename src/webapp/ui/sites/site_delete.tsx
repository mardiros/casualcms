import React from "react";
import { Navigate } from "react-router-dom";
import { Site } from "../../casualcms/domain/model";
import { AppContext } from "../../config";
import { DeletePopoverForm } from "../layout/confirm";
import { useAuth } from "../login/hooks";

type SiteDeletePopoverFormProps = {
  curSite: Site;
};

export const SiteDeletePopoverForm: React.FunctionComponent<
  SiteDeletePopoverFormProps
> = (props: SiteDeletePopoverFormProps) => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const curSite = props.curSite;

  const [confirmed, setConfirmed] = React.useState<boolean>(false);

  const onSubmit = async () => {
    await config.api.site.deleteSite(token, curSite.hostname);
    setConfirmed(true);
  };

  if (confirmed) {
    return <Navigate to="/admin/sites" replace />;
  }

  return (
    <DeletePopoverForm button_label="Delete this site" onSubmit={onSubmit} />
  );
};
